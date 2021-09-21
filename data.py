import glob
import tarfile
import csv
import json
import fnmatch
import codecs
import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Generator, BinaryIO, Callable, Union

import pandas as pd
import numpy as np


IsoWeek = Tuple[int, int]


class Data:

    PATH = Path(__file__).resolve().parent / "compressed"

    def __init__(
            self,
            include: Optional[str] = None,
            exclude: Optional[str] = None,
            iso_week_gt: Optional[IsoWeek] = None,
            iso_week_gte: Optional[IsoWeek] = None,
            iso_week_lt: Optional[IsoWeek] = None,
            iso_week_lte: Optional[IsoWeek] = None,
    ):
        self.include = include
        self.exclude = exclude
        self.iso_week_gt = iso_week_gt
        self.iso_week_gte = iso_week_gte
        self.iso_week_lt = iso_week_lt
        self.iso_week_lte = iso_week_lte
        self._meta = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.filter()})"

    @property
    def meta(self):
        if self._meta is None:
            with open(self.PATH / "metadata.json") as fp:
                self._meta = json.load(fp)
        return self._meta

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

    def filter(self) -> str:
        """Returns current filter as string"""
        return ", ".join(
            f"{name}={getattr(self, name)}"
            for name in (
                "include", "exclude",
                "iso_week_gt", "iso_week_gte", "iso_week_lt", "iso_week_lte"
            )
            if getattr(self, name)
        )

    def get_meta(self, source_id: str, location_id: str, value_name: Optional[str] = None, default=None):
        if value_name is None:
            return self.meta.get(source_id, {}).get(location_id, default)
        return self.meta.get(source_id, {}).get("locations", {}).get(location_id, {}).get(value_name, default)

    def compressed_files(self) -> List[Tuple[IsoWeek, str]]:
        """
        Returns a list of all compressed files and their associated iso week tuple
        """
        rows = []
        for fn in sorted(glob.glob(str(self.PATH / "*" / "*.tar.gz"))):
            iso_week = self.string_to_iso_week(Path(fn).name.split(".")[0])

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
                    if self.exclude and fnmatch.fnmatchcase(id_name, self.exclude):
                        continue
                    if self.include and not fnmatch.fnmatchcase(id_name, self.include):
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
            fp = codecs.getreader("utf-8")(fp)
            rows = list(csv.reader(fp))
            columns = rows[0]
            rows = rows[1:]

            for row in rows:
                if as_datetime:
                    row[0] = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
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
            yield iso_week, id, columns, rows

    def iter_dataframes(self) -> Generator[Tuple[IsoWeek, str, pd.DataFrame], None, None]:
        for iso_week, id, columns, rows in self.iter_tables(as_int=True):
            df = pd.DataFrame(rows, columns=columns)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index(["date", "source_id", "location_id"], inplace=True)

            yield iso_week, id, df


class Metrics:

    PATH = Path(__file__).resolve().parent / "metrics"

    @classmethod
    def snapshots_weekly(cls) -> pd.DataFrame:
        """
        Returns a DataFrame from the "snapshots-weekly.csv"
        """
        df = (
            pd.read_csv(cls.PATH / "snapshots-weekly.csv")
            .set_index(["weeks", "location_id"])
        )
        df["min_date"] = pd.to_datetime(df["min_date"])
        df["max_date"] = pd.to_datetime(df["max_date"])
        return df

    @classmethod
    def snapshots_sum(cls) -> pd.DataFrame:
        """
        Returns a DataFrame from the "snapshots-sum.csv"
        """
        df = (
            pd.read_csv(cls.PATH / "snapshots-sum.csv")
            .set_index("source_id")
        )
        df["min_date"] = pd.to_datetime(df["min_date"])
        df["max_date"] = pd.to_datetime(df["max_date"])
        return df

    @classmethod
    def appointments(
            cls,
            source_id: Optional[Union[str, Callable]] = None,
            location_id: Optional[Union[str, Callable]] = None,
            iso_week_gt: Optional[IsoWeek] = None,
            iso_week_gte: Optional[IsoWeek] = None,
            iso_week_lt: Optional[IsoWeek] = None,
            iso_week_lte: Optional[IsoWeek] = None,
            as_int: bool = False,
    ) -> pd.DataFrame:
        """
        Returns a DataFrame with all appointments per snapshot time.

        :param source_id: optional filter, either exact string or a callable returning bool
        :param location_id: optional filter, either exact string or a callable returning bool
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
        return cls._changes(
            type="appointments",
            source_id=source_id,
            location_id=location_id,
            iso_week_gt=iso_week_gt,
            iso_week_gte=iso_week_gte,
            iso_week_lt=iso_week_lt,
            iso_week_lte=iso_week_lte,
            as_int=as_int,
        )

    @classmethod
    def _changes(
            cls,
            type: str,
            source_id: Optional[str] = None,
            location_id: Optional[str] = None,
            iso_week_gt: Optional[IsoWeek] = None,
            iso_week_gte: Optional[IsoWeek] = None,
            iso_week_lt: Optional[IsoWeek] = None,
            iso_week_lte: Optional[IsoWeek] = None,
            as_int: bool = False,
    ) -> pd.DataFrame:
        dataframes = []
        for filename in sorted(glob.glob(str(cls.PATH / type / "*" / "*.csv"))):
            week = Data.string_to_iso_week(Path(filename).name.split(".")[0])
            if iso_week_gt and not week > iso_week_gt:
                continue
            if iso_week_gte and not week >= iso_week_gte:
                continue
            if iso_week_lt and not week < iso_week_lt:
                break
            if iso_week_lte and not week <= iso_week_lte:
                break

            df = pd.read_csv(filename).set_index("date")
            dataframes.append(df)

        df = pd.concat(dataframes)

        if source_id:
            if callable(source_id):
                df = df.loc[:, [c for c in df.columns if source_id(c)]]
            else:
                df = df.loc[:, [c for c in df.columns if c.startswith(source_id + "/")]]

        if location_id:
            if callable(location_id):
                df = df.loc[:, [c for c in df.columns if location_id(c)]]
            else:
                df = df.loc[:, [c for c in df.columns if c.endswith("/" + location_id)]]

        if as_int:
            df = df.replace(np.nan, 0).astype(int)

        df.sort_index(inplace=True)
        df.sort_index(inplace=True, axis=1)
        df.index = pd.to_datetime(df.index)

        return df
