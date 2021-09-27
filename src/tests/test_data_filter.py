import unittest

from src.data import *


class TestDataFilter(unittest.TestCase):

    def test_get_table(self):
        self.assertEqual(
            ["fuhrerscheinwesen", "kfz-zulassungswesen", "meldewesen"],
            sorted(Data.get_dataframe((2021, 28), "bonn").index.get_level_values("location_id").unique())
        )
        self.assertEqual(
            ["meldewesen"],
            sorted(Data.get_dataframe((2021, 28), "bonn", "meldewesen").index.get_level_values("location_id").unique())
        )
        self.assertEqual(
            ["kfz-zulassungswesen", "meldewesen"],
            sorted(Data.get_dataframe((2021, 28), "bonn", ["meldewesen", "kfz*"]).index.get_level_values("location_id").unique())
        )

    def test_iter_files(self):
        self.assertEqual(
            [((2021, 28), "bonn")],
            list((week, source_id) for week, source_id, fp in Data(
                include="bonn", iso_week=(2021, 28)
            ).iter_files())
        )
        self.assertEqual(
            [((2021, 28), "bonn"), ((2021, 29), "bonn")],
            list((week, source_id) for week, source_id, fp in Data(
                include="bonn", iso_week_lte=(2021, 29)
            ).iter_files())
        )
        self.assertEqual(
            [((2021, 28), "bonn"), ((2021, 28), "jena")],
            list((week, source_id) for week, source_id, fp in Data(
                include=["bonn", "jena"], iso_week=(2021, 28)
            ).iter_files())
        )
        self.assertEqual(
            [((2021, 28), "bonn"), ((2021, 28), "bonnbau"), ((2021, 28), "jena")],
            list((week, source_id) for week, source_id, fp in Data(
                include=["b*", "jena"], iso_week=(2021, 28)
            ).iter_files())
        )

if __name__ == "__main__":
    unittest.main()
