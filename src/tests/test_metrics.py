import unittest

from src.data import *
#from src.metrics_calc import _is_in_timespan, calc_metrics


class TestMetrics(unittest.TestCase):

    def X_test_in_timespan(self):
        self.assertTrue(_is_in_timespan(
            ("in_1h", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 0, 50)
        ))
        self.assertTrue(_is_in_timespan(
            ("in_1h", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 1, 0)
        ))
        self.assertFalse(_is_in_timespan(
            ("in_1h", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 1, 1)
        ))
        self.assertTrue(_is_in_timespan(
            ("in_1d", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 2, 0, 0)
        ))
        self.assertFalse(_is_in_timespan(
            ("in_1d", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 2, 0, 1)
        ))
        self.assertTrue(_is_in_timespan(
            ("in_2w", 14), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 15, 0, 0)
        ))
        self.assertFalse(_is_in_timespan(
            ("in_2w", 14), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 15, 0, 1)
        ))

    def X_test_at_timespan(self):
        self.assertTrue(_is_in_timespan(
            ("at_1h", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 0, 59)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_1h", 1), datetime.datetime(2000, 1, 1, 0, 30), datetime.datetime(2000, 1, 1, 0, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_1h", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 1, 0)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_3h", 3), datetime.datetime(2000, 1, 1, 0, 30), datetime.datetime(2000, 1, 1, 2, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_3h", 3), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 3, 0)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_1d", 1), datetime.datetime(2000, 1, 1, 0, 30), datetime.datetime(2000, 1, 1, 23, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_1d", 1), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 2, 0, 0)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_3d", 3), datetime.datetime(2000, 1, 1, 0, 30), datetime.datetime(2000, 1, 3, 23, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_3d", 3), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 4, 0, 0)
        ))
        # 1999-12-27 / 2000-01-03 is a monday
        self.assertTrue(_is_in_timespan(
            ("at_1w", 7), datetime.datetime(1999, 12, 27, 0, 0), datetime.datetime(2000, 1, 2, 23, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_1w", 7), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 3, 0, 0)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_2w", 14), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 3, 0, 0)
        ))
        self.assertTrue(_is_in_timespan(
            ("at_2w", 14), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 9, 23, 59)
        ))
        self.assertFalse(_is_in_timespan(
            ("at_2w", 14), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 10, 0, 0)
        ))

    def test_metrics(self):
        # something that does not exist returns None
        df = Metrics.dataframe("appointments", iso_week_lte=(2000, 1))
        self.assertIsNone(df)

        df = Metrics.dataframe(
            #"appointments",
            iso_week=(2021, 28),
        )
        print(df)


if __name__ == "__main__":
    unittest.main()
