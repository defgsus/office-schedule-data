import os
import argparse
from io import StringIO, BytesIO
import warnings
from multiprocessing import Pool
from tqdm import tqdm

from src.data import *
from src.metrics_calc import calc_metrics

PATH: Path = Path(__file__).resolve().parent.parent
METRICS_PATH = PATH / "metrics"

SNAPSHOTS_WEEKLY_FILE = METRICS_PATH / "summary-weekly.csv"
SNAPSHOTS_SUM_FILE = METRICS_PATH / "summary.csv"


def update_metrics(
        force_recalc: bool = False,
        processes: int = 1,
        source_id: StringFilter = None,
):
    iso_weeks = [f[0] for f in Data().compressed_files()]
    assert iso_weeks, "no data found"

    base_filter = {"source_id": source_id}

    weeks_to_calc = []
    for week in iso_weeks:
        path = METRICS_PATH / str(week[0])
        filename = path / f"{Data.iso_week_to_string(week)}.tar.gz"

        if force_recalc or not filename.exists():
            data_filter = base_filter.copy()
            data_filter["iso_week"] = week
            weeks_to_calc.append((data_filter, path, filename))
        else:
            print(f"{filename} already exists")

    if not weeks_to_calc:
        return

    if processes <= 1:
        stash = dict()
        for data_filter, path, filename in weeks_to_calc:
            data = Data(**data_filter)
            metrics = calc_metrics(data, stash=stash)
            _store_metrics(metrics, path, filename)
    else:
        warnings.warn(
            "Metrics with processes > 1 is only for development and not suited "
            "for publishing. Each week should be analyzed in sequence."
        )
        pool = Pool(processes)
        pool.map(_calc_metric_process, weeks_to_calc)


def _calc_metric_process(arg):
    data_filter, path, filename = arg
    data = Data(**data_filter)
    metrics = calc_metrics(data, stash=None)
    _store_metrics(metrics, path, filename)


def _store_metrics(metrics: Dict[str, pd.DataFrame], path: Path, filename: Path):
    print(f"compressing metrics into {filename}")
    os.makedirs(path, exist_ok=True)
    with tarfile.open(filename, "w:gz") as tf:
        for name, df in metrics.items():
            bin = df.to_csv().encode("utf-8")
            bin_file = BytesIO(bin)

            info = tarfile.TarInfo(f"{name}.csv")
            info.size = len(bin)
            tf.addfile(info, bin_file)


def calc_weekly_summary(data: Data) -> Optional[pd.DataFrame]:
    print(f"calc weekly summary of {data}")

    df_changes = dict()
    for change_type in ("appointments", "cancellations"):
        df = Metrics.dataframe(
            type=change_type,
            iso_week=data.iso_week,
            iso_week_gt=data.iso_week_gt,
            iso_week_gte=data.iso_week_gte,
            iso_week_lt=data.iso_week_lt,
            iso_week_lte=data.iso_week_lte,
            as_int=True,
        )
        if df is not None:
            # hard clip on appointments data
            #   to throw out the complicated and nonsense stuff
            df = df.clip(0, 1)
            df["week"] = df.index.map(lambda d: d.isocalendar()[:2])
            df = df.groupby("week").sum()

        df_changes[change_type] = df

    stat_rows = []
    for iso_week, source_id, columns, rows in tqdm(data.iter_tables(as_int=False)):

        changes = 0
        prev_dates_free = dict()
        for row in rows:
            loc_id = row[2]
            dates_free = row[3:]
            if loc_id in prev_dates_free:
                if prev_dates_free[loc_id] != dates_free:
                   changes += 1

            prev_dates_free[loc_id] = dates_free

        num_changes = {f"num_{change_type}": -1 for change_type in df_changes}
        for change_type in df_changes:
            if df_changes[change_type] is not None:
                df = df_changes[change_type]
                # filter this iso-week
                df = df[df.index == iso_week]
                # filter this source_id
                df = df.loc[:, [c for c in df.columns if c.startswith(f"{source_id}/")]]
                # get the sum
                num_changes[f"num_{change_type}"] = df.sum().sum()

        stat_rows.append({
            "week": "%s-%02d" % iso_week,
            "source_id": source_id,
            "num_locations": len(set(row[2] for row in rows)),
            "num_snapshots": len(set(row[0] for row in rows)),
            "num_changes": changes,
            **num_changes,
            "min_date": min(row[0] for row in rows),
            "max_date": max(row[0] for row in rows),
        })

    if not stat_rows:
        return None
    df = pd.DataFrame(stat_rows)
    df.set_index(["week", "source_id"], inplace=True)
    return df


def update_weekly_summary(
        force_recalc: bool = False,
):
    filename = SNAPSHOTS_WEEKLY_FILE

    previous_stats = None
    data = Data()  # full run over all weeks

    if not force_recalc:
        try:
            previous_stats = (
                pd.read_csv(filename)
                .set_index(["week", "source_id"])
            )
            max_date = previous_stats.index.get_level_values("week").max()
            max_date = Data.string_to_iso_week(max_date)

            data = Data(iso_week_gt=max_date)

        except Exception as e:
            previous_stats = None

    stats = calc_weekly_summary(data)
    if stats is None and previous_stats is not None:
        print(f"unchanged: {filename}")
        return

    if previous_stats is not None:
        stats = pd.concat([previous_stats, stats])

    print(f"writing weekly summary {filename}")
    stats.to_csv(filename)


def update_summary_and_readme():
    print("updating summary")
    data = Data()

    sn_df = pd.read_csv(SNAPSHOTS_WEEKLY_FILE)
    print(sn_df.to_markdown())
    source_group = sn_df.groupby("source_id")
    df = source_group.sum()
    df["num_locations"] = (source_group["num_locations"].mean() + .5).astype(np.int)
    #df = df[df.columns[-2:].append(df.columns[:-2])]
    df["min_date"] = source_group["min_date"].min()
    df["max_date"] = source_group["max_date"].max()
    df["scraper"] = df.index.map(lambda source_id: data.get_meta(source_id, "scraper", default="-"))
    df["name"] = df.index.map(lambda source_id: data.get_meta(source_id, "name", default="-"))
    print(df.to_markdown())
    df.to_csv(SNAPSHOTS_SUM_FILE)

    df.index = df.index.map(lambda source_id: (
        f"[{source_id}]({data.get_meta(source_id, 'url')})" if data.get_meta(source_id, "url") else source_id
    ))

    template_context = {
        "last_exported_date": df["max_date"].max()[:10],
        "metrics_date": datetime.date.today(),
        "num_sources": format(df.index.nunique(), ","),
        "num_locations": format(df["num_locations"].sum(), ","),
        "num_snapshots": format(df["num_snapshots"].sum(), ","),
        "num_appointments": format(df["num_appointments"].sum(), ","),
        "metric_sum_table": df.to_markdown(),
    }

    readme = (PATH / "templates" / "README.md").read_text()
    readme = readme % template_context
    (PATH / "README.md").write_text(readme)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-metrics", type=bool, nargs="?", default=False, const=True,
        help="Force recalculation of all metrics (takes a long time!)",
    )
    parser.add_argument(
        "--force-weekly", type=bool, nargs="?", default=False, const=True,
        help="Force recalculation of weekly summary",
    )
    parser.add_argument(
        "--processes", type=int, nargs="?", default=1,
        help="Number of parallel processes (for each week) - for development only!",
    )
    parser.add_argument(
        "--source", type=str, nargs="+", default=None,
        help="Filter for source_id - for development only!",
    )

    args = parser.parse_args()

    update_metrics(
        force_recalc=args.force_metrics,
        processes=args.processes,
        source_id=args.source,
    )
    update_weekly_summary(
        force_recalc=args.force_weekly,
    )
    update_summary_and_readme()


if __name__ == "__main__":
    main()
