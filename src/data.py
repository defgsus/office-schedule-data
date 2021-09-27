import glob
import tarfile
import csv
import json
import fnmatch
import codecs
import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Generator, BinaryIO, Callable, Union, Dict, Sequence

import pandas as pd
import numpy as np


IsoWeek = Tuple[int, int]
StringFilter = Optional[Union[str, Sequence[str], Callable[[str], bool]]]


def to_datetime(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


class Data:

    PATH = Path(__file__).resolve().parent.parent / "raw"
    _meta = None

    def __init__(
            self,
            source_id: StringFilter = None,
            source_id_not: StringFilter = None,
            iso_week: Optional[IsoWeek] = None,
            iso_week_gt: Optional[IsoWeek] = None,
            iso_week_gte: Optional[IsoWeek] = None,
            iso_week_lt: Optional[IsoWeek] = None,
            iso_week_lte: Optional[IsoWeek] = None,
    ):
        self.source_id = source_id
        self.source_id_not = source_id_not
        self.iso_week = iso_week
        self.iso_week_gt = iso_week_gt
        self.iso_week_gte = iso_week_gte
        self.iso_week_lt = iso_week_lt
        self.iso_week_lte = iso_week_lte

    def __str__(self):
        return f"{self.__class__.__name__}({self.filter()})"

    @classmethod
    def meta(cls) -> dict:
        if cls._meta is None:
            with open(cls.PATH / "metadata.json") as fp:
                cls._meta = json.load(fp)
        return cls._meta

    @classmethod
    def get_meta(
            cls,
            source_id: str,
            location_id: Optional[str] = None,
            value_name: Optional[str] = None,
            *, default=None
    ):
        data = cls.meta().get(source_id, {})
        if location_id is None:
            return data or default

        locations = data.get("locations", {})
        if value_name is None:
            if location_id in locations:
                return locations[location_id]
            return data.get(location_id, default)

        return locations.get(location_id, {}).get(value_name, default)

    @classmethod
    def string_to_iso_week(cls, s: str) -> IsoWeek:
        iso_week = s.split("-")
        return (
            int(iso_week[0]),
            int(iso_week[1].lstrip("0"))
        )

    @classmethod
    def iso_week_to_string(cls, week: Tuple[int, int]) -> str:
        return f"{week[0]:04d}-{week[1]:02d}"

    @classmethod
    def string_to_datetime(cls, s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_table(
            cls,
            iso_week: IsoWeek,
            source_id: str,
            location_id: StringFilter = None,
            as_int: bool = False,
            as_datetime: bool = False,
            empty: Optional[str] = None,
            with_meta: bool = False,
    ) -> Tuple[List, List[List]]:
        iso_week_str = cls.iso_week_to_string(iso_week)

        with tarfile.open(cls.PATH / iso_week_str[:4] / f"{iso_week_str}.tar.gz") as tf:
            fp = tf.extractfile(f"{source_id}.csv")
            columns, rows = cls._read_table(fp=fp, as_int=as_int, as_datetime=as_datetime, empty=empty)

            if location_id is not None:
                rows = [
                    row for row in rows
                    if _string_filter(row[2], location_id)
                ]

            if with_meta:
                rows = [
                    row[:3] + [cls.get_meta(row[1], "name"), cls.get_meta(row[1], row[2], "name")] + row[3:]
                    for row in rows
                ]
                columns = columns[:3] + ["source_name", "location_name"] + columns[3:]

            return columns, rows

    @classmethod
    def get_dataframe(
            cls,
            iso_week: Tuple[int, int],
            source_id: str,
            location_id: StringFilter = None,
            as_datetime: bool = True,
            with_meta: bool = False,
    ) -> pd.DataFrame:
        columns, rows = cls.get_table(
            iso_week=iso_week, 
            source_id=source_id, location_id=location_id,
            as_int=True, as_datetime=as_datetime,
            with_meta=with_meta,
        )
        return cls._table_to_dataframe(columns, rows, as_datetime=as_datetime)

    def filter(self) -> str:
        """Returns current filter as string"""
        return ", ".join(
            f"{name}={getattr(self, name)}"
            for name in (
                "source_id", "source_id_not",
                "iso_week", "iso_week_gt", "iso_week_gte", "iso_week_lt", "iso_week_lte"
            )
            if getattr(self, name)
        )

    def compressed_files(self) -> List[Tuple[IsoWeek, str]]:
        """
        Returns a list of all compressed files and their associated iso week tuple
        """
        rows = []
        for fn in sorted(glob.glob(str(self.PATH / "*" / "*.tar.gz"))):
            iso_week = self.string_to_iso_week(Path(fn).name.split(".")[0])

            if self.iso_week and iso_week != self.iso_week:
                continue
            if self.iso_week_gt and not (iso_week > self.iso_week_gt):
                continue
            if self.iso_week_gte and not (iso_week >= self.iso_week_gte):
                continue
            if self.iso_week_lt and not iso_week < self.iso_week_lt:
                continue
            if self.iso_week_lte and not iso_week <= self.iso_week_lte:
                continue

            rows.append((iso_week, fn))
        return rows

    def iter_files(self) -> Generator[Tuple[IsoWeek, str, BinaryIO], None, None]:
        """
        Iterates through all csv files inside the compressed tars.
        :return: generates tuples of iso-week, id-name, binary file-io
        """
        for iso_week, tar_filename in self.compressed_files():
            with tarfile.open(tar_filename) as tf:
                for csv_name in sorted(tf.getnames()):
                    id_name = csv_name.split(".")[0]
                    if self.source_id_not and _string_filter(id_name, self.source_id_not):
                        continue
                    if self.source_id and not _string_filter(id_name, self.source_id):
                        continue

                    fp = tf.extractfile(csv_name)
                    if fp:
                        yield iso_week, id_name, fp

    def iter_tables(
            self,
            as_int: bool = True,
            as_datetime: bool = False,
            empty: Optional[str] = None,
    ) -> Generator[Tuple[IsoWeek, str, List[str], List[List]], None, None]:
        """
        Iterate through all tables in the dataset.

        :param as_int: bool, convert "1" and "" into 1 and 0
        :param as_datetime: bool, convert first column to datetime
        :param empty: str, optionally replace "" with another string, supersedes 'as_int'
        :return: generates tuples of (iso_week, source_id, list of columns, list of rows)
        """
        for iso_week, id, fp in self.iter_files():
            columns, rows = self._read_table(fp=fp, as_int=as_int, as_datetime=as_datetime, empty=empty)
            yield iso_week, id, columns, rows

    def iter_dataframes(
            self,
            as_datetime: bool = True,
    ) -> Generator[Tuple[IsoWeek, str, pd.DataFrame], None, None]:
        for iso_week, id, columns, rows in self.iter_tables(as_int=True):
            df = self._table_to_dataframe(columns, rows, as_datetime=as_datetime)
            yield iso_week, id, df

    @classmethod
    def _table_to_dataframe(cls, columns, rows, as_datetime: bool) -> pd.DataFrame:
        df = pd.DataFrame(rows, columns=columns)
        if as_datetime:
            df["date"] = pd.to_datetime(df["date"])

        index_columns = ["date", "source_id", "location_id"]
        if "source_name" in columns:
            index_columns += ["source_name", "location_name"]
        df.set_index(index_columns, inplace=True)

        return df

    @classmethod
    def _read_table(
            cls,
            fp: BinaryIO,
            as_int: bool = False,
            as_datetime: bool = False,
            empty: Optional[str] = None,
    ) -> Tuple[List, List[List]]:
        fp = codecs.getreader("utf-8")(fp)
        rows = list(csv.reader(fp))
        columns = rows[0]
        rows = rows[1:]

        if as_datetime:
            for i in range(3, len(columns)):
                columns[i] = cls.string_to_datetime(columns[i])

        for row in rows:
            if as_datetime:
                row[0] = cls.string_to_datetime(row[0])
            # make location_id always str
            row[2] = str(row[2])

        if empty is not None:
            rows = [
                row[:3] + [empty if v == "" else v for v in row[3:]]
                for row in rows
            ]
        elif as_int:
            rows = [
                row[:3] + [0 if v == "" else 1 for v in row[3:]]
                for row in rows
            ]
        return columns, rows


class Metrics:

    PATH = Path(__file__).resolve().parent.parent / "metrics"

    @classmethod
    def summary_weekly(cls) -> pd.DataFrame:
        """
        Returns a DataFrame from the "summary-weekly.csv"
        """
        df = (
            pd.read_csv(cls.PATH / "summary-weekly.csv")
            .set_index(["week", "source_id"])
        )
        df["min_date"] = pd.to_datetime(df["min_date"])
        df["max_date"] = pd.to_datetime(df["max_date"])
        return df

    @classmethod
    def summary(cls) -> pd.DataFrame:
        """
        Returns a DataFrame from the "summary.csv"
        """
        df = (
            pd.read_csv(cls.PATH / "summary.csv")
            .set_index("source_id")
        )
        df["min_date"] = pd.to_datetime(df["min_date"])
        df["max_date"] = pd.to_datetime(df["max_date"])
        return df

    @classmethod
    def dataframe(
            cls,
            type: StringFilter = None,
            source_id: StringFilter = None,
            location_id: StringFilter = None,
            iso_week: Optional[IsoWeek] = None,
            iso_week_gt: Optional[IsoWeek] = None,
            iso_week_gte: Optional[IsoWeek] = None,
            iso_week_lt: Optional[IsoWeek] = None,
            iso_week_lte: Optional[IsoWeek] = None,
            as_int: bool = False,
            multiindex: bool = False,
            with_meta: bool = False,
    ) -> Optional[pd.DataFrame]:
        """
        Returns a pandas.DataFrame with all calculated metrics.

        The metrics can optionally be filtered by type, source_id, location_id and weeks.

        :param type: optional filter, either wildcard string, or list of wildcard strings or
            a callable(str) returning bool
        :param source_id: optional filter, either wildcard string or a callable(str) returning bool
        :param location_id: optional filter, either wildcard string or a callable(str) returning bool
        :param iso_week: optional filter for the week (exact match)
        :param iso_week_gt: optional filter for the week (greater than)
        :param iso_week_gte: optional filter for the week (greater than or equal)
        :param iso_week_lt: optional filter for the week (less than)
        :param iso_week_lte: optional filter for the week (less than or equal)
        :param as_int: bool
            if True: all numbers are int
            if False: numbers are float and unfilled numbers (where no snapshot data was
            available) is NaN.
        :return: pandas DataFrame
        """
        dataframes_weeks = []

        for filename in sorted(glob.glob(str(cls.PATH / "????" / "*.tar.gz"))):
            week = Data.string_to_iso_week(Path(filename).name.split(".")[0])
            if iso_week and week != iso_week:
                continue
            if iso_week_gt and not week > iso_week_gt:
                continue
            if iso_week_gte and not week >= iso_week_gte:
                continue
            if iso_week_lt and not week < iso_week_lt:
                break
            if iso_week_lte and not week <= iso_week_lte:
                break

            dataframes = dict()
            with tarfile.open(filename) as tf:
                for csv_name in tf.getnames():
                    type_name = csv_name.split(".")[0]
                    if not _string_filter(type_name, type):
                        continue
                    #print("reading", filename, week, type)
                    fp = tf.extractfile(csv_name)
                    df = pd.read_csv(fp).set_index("date")
                    #df.replace(np.nan, 0, inplace=True)
                    df.columns = [f"{c}/{type_name}" for c in df.columns]
                    dataframes[type_name] = df

            if dataframes:
                df = pd.concat(dataframes.values(), axis=1)
                dataframes_weeks.append(df)

        if not dataframes_weeks:
            return

        df = pd.concat(dataframes_weeks)

        if source_id:
            df = df.loc[:, [c for c in df.columns if _string_filter(c.split("/")[0], source_id)]]
        if location_id:
            df = df.loc[:, [c for c in df.columns if _string_filter(c.split("/")[1], location_id)]]

        if as_int:
            df.replace(np.nan, 0, inplace=True)
            df = df.astype(int)

        df.sort_index(inplace=True)
        df.sort_index(inplace=True, axis=1)
        df.index = pd.to_datetime(df.index)

        if multiindex:
            cols = [c.split("/") for c in df.columns]
            if with_meta:
                cols = [
                    [
                        Data.get_meta(c[0], "name") or c[0],
                        Data.get_meta(c[0], c[1], "name") or c[1],
                        c[2]
                    ]
                    for c in cols
                ]

            source_ids = sorted(set(c[0] for c in cols))
            location_ids = sorted(set(c[1] for c in cols))
            type_ids = sorted(set(c[2] for c in cols))
            df.columns = pd.MultiIndex(
                [source_ids, location_ids, type_ids],
                [
                    [source_ids.index(c[0]) for c in cols],
                    [location_ids.index(c[1]) for c in cols],
                    [type_ids.index(c[2]) for c in cols],
                ],
                names=["source", "location", "metric"],
            )
        return df


def _string_filter(s: str, f: StringFilter):
    if f is None:
        return True
    if isinstance(f, str):
        return fnmatch.fnmatchcase(s, f)
    elif isinstance(f, Sequence):
        return any(fnmatch.fnmatchcase(s, x) for x in f)
    elif callable(f):
        return f(s)
    else:
        raise TypeError(f"Invalid filter type '{type(f).__name__}'")
