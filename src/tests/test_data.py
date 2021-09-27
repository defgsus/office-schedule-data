import unittest

from src.data import *


class TestData(unittest.TestCase):

    def test_meta(self):
        d = Data.get_meta("bonn")
        self.assertIsInstance(d, dict)
        self.assertEqual("Stadt Bonn", d["name"])

        self.assertEqual("Stadt Bonn", Data.get_meta("bonn", "name"))
        self.assertEqual("Führerscheinwesen", Data.get_meta("bonn", "fuhrerscheinwesen", "name"))

        d = Data.get_meta("bonn", "fuhrerscheinwesen")
        self.assertIsInstance(d, dict)
        self.assertEqual("Führerscheinwesen", d["name"])

    def test_get_table(self):
        columns, rows = Data.get_table((2021, 28), "bonn")
        self.assertEqual(
            ["date", "source_id", "location_id", "2021-07-12 08:20:00"],
            columns[:4]
        )
        self.assertEqual(
            ["2021-07-12 00:03:33", "bonn", "fuhrerscheinwesen", "", "", ""],
            rows[0][:6]
        )
        # the rest must be datetimes
        [datetime.datetime.strptime(c, "%Y-%m-%d %H:%M:%S") for c in columns[3:]]

    def test_get_table_int_and_datetime(self):
        columns, rows = Data.get_table((2021, 28), "bonn", as_int=True, as_datetime=True)
        self.assertEqual(
            ["date", "source_id", "location_id", datetime.datetime(2021, 7, 12, 8, 20, 0)],
            columns[:4]
        )
        self.assertEqual(
            [datetime.datetime(2021, 7, 12, 0, 3, 33), "bonn", "fuhrerscheinwesen", 0, 0, 0],
            rows[0][:6]
        )
        self.assertTrue(any(isinstance(row[0], datetime.datetime) for row in rows))
        self.assertTrue(any(isinstance(d, datetime.datetime) for d in columns[3:]))

    def test_get_table_meta(self):
        columns, rows = Data.get_table((2021, 28), "bonn", with_meta=True)
        self.assertEqual(
            ["date", "source_id", "location_id", "source_name", "location_name", "2021-07-12 08:20:00"],
            columns[:6]
        )
        self.assertEqual(
            ["2021-07-12 00:03:33", "bonn", "fuhrerscheinwesen", "Stadt Bonn", "Führerscheinwesen", "", "", ""],
            rows[0][:8]
        )
        # the rest must be datetimes
        [datetime.datetime.strptime(c, "%Y-%m-%d %H:%M:%S") for c in columns[5:]]

    def test_get_table_meta_int_and_datetime(self):
        columns, rows = Data.get_table((2021, 28), "bonn", as_int=True, as_datetime=True, with_meta=True)
        self.assertEqual(
            ["date", "source_id", "location_id", "source_name", "location_name",
             datetime.datetime(2021, 7, 12, 8, 20, 0)],
            columns[:6]
        )
        self.assertEqual(
            [datetime.datetime(2021, 7, 12, 0, 3, 33),
             "bonn", "fuhrerscheinwesen", "Stadt Bonn", "Führerscheinwesen", 0, 0, 0],
            rows[0][:8]
        )
        self.assertTrue(any(isinstance(row[0], datetime.datetime) for row in rows))
        self.assertTrue(any(isinstance(d, datetime.datetime) for d in columns[5:]))

    def test_get_dataframe(self):
        df = Data.get_dataframe((2021, 28), "bonn")
        self.assertEqual(
            ["date", "source_id", "location_id"],
            df.index.names
        )
        # columns are only dates
        self.assertEqual(
            [datetime.datetime(2021, 7, 12, 8, 20, 0),
             datetime.datetime(2021, 7, 12, 8, 25, 0),
             datetime.datetime(2021, 7, 12, 8, 30, 0)],
            df.columns[:3].to_list()
        )
        self.assertEqual(
            [0, 0, 0],
            df.iloc[:3, 0].to_list()
        )
        self.assertEqual(
            (pd.Timestamp(2021, 7, 12, 0, 3, 33), "bonn", "fuhrerscheinwesen"),
            df.index[0],
        )

    def test_get_dataframe_no_datetime(self):
        df = Data.get_dataframe((2021, 28), "bonn", as_datetime=False)
        self.assertEqual(
            ["2021-07-12 08:20:00", "2021-07-12 08:25:00", "2021-07-12 08:30:00"],
            df.columns[:3].to_list()
        )
        self.assertEqual(
            ("2021-07-12 00:03:33", "bonn", "fuhrerscheinwesen"),
            df.index[0],
        )

    def test_get_dataframe_meta(self):
        df = Data.get_dataframe((2021, 28), "bonn", with_meta=True)
        self.assertEqual(
            ["date", "source_id", "location_id", "source_name", "location_name"],
            df.index.names
        )
        # columns are only dates
        self.assertEqual(
            [datetime.datetime(2021, 7, 12, 8, 20, 0),
             datetime.datetime(2021, 7, 12, 8, 25, 0),
             datetime.datetime(2021, 7, 12, 8, 30, 0)],
            df.columns[:3].to_list()
        )
        self.assertEqual(
            [0, 0, 0],
            df.iloc[:3, 0].to_list()
        )
        self.assertEqual(
            (pd.Timestamp(2021, 7, 12, 0, 3, 33), "bonn", "fuhrerscheinwesen", "Stadt Bonn", "Führerscheinwesen"),
            df.index[0],
        )


if __name__ == "__main__":
    unittest.main()
