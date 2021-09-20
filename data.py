import glob
import tarfile
import csv
import json
import fnmatch
import codecs
import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Generator, BinaryIO

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
    ):
        self.include = include
        self.exclude = exclude
        self.iso_week_gt = iso_week_gt
        self.iso_week_gte = iso_week_gte
        self.iso_week_lt = iso_week_lt
        self._meta = None

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

    def filter(self):
        return ", ".join(
            f"{name}={getattr(self, name)}"
            for name in (
                "include", "exclude", "iso_week_gt", "iso_week_gte", "iso_week_lt"
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

            if self.iso_week_gt and not (iso_week > self.iso_week_gt):
                continue
            if self.iso_week_gte and not (iso_week >= self.iso_week_gte):
                continue
            if self.iso_week_lt and iso_week >= self.iso_week_lt:
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
