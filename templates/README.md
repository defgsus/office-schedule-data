## History of free office appointment dates (in Germany)

This is the data export of [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/).

The data contains the **free dates** where one can make an appointment at a 
public office at a snapshot interval of 15 minutes, starting at 2021-07-12.

This data repository is updated weekly and the most recent timestamp 
is on **%(last_exported_date)s**.


# Data layout

The [compressed](compressed) folder contains **tar.gz** files for each 
calendar week wherein are **csv** files for each scraped website. Those have the
following format:

| date                | source_id | location_id | 2021-07-12 08:00:00 | 2021-07-12 08:05:00 | ... |
|:--------------------|:----------|------------:|--------------------:|--------------------:|----:|
| 2021-07-12 00:04:23 | jena      |         197 |                   1 |                     | ... |
| 2021-07-12 00:04:23 | jena      |         198 |                     |                   1 | ... |
| 2021-07-12 00:04:23 | jena      |         199 |                     |                   1 | ... |
| 2021-07-12 00:04:23 | jena      |         200 |                   1 |                     | ... |
| 2021-07-12 00:19:27 | jena      |         197 |                   1 |                     | ... |
| 2021-07-12 00:19:27 | jena      |         198 |                     |                   1 | ... |
| 2021-07-12 00:19:27 | jena      |         199 |                     |                   1 | ... |
| 2021-07-12 00:19:27 | jena      |         200 |                   1 |                     | ... |
| ...                 | ...       |         ... |                 ... |                 ... | ... |

- The `date` column represents the timestamp of the snapshot
  - All dates are (very probably) in `Europe/Berlin` timezone.
- The `source_id` columns contains the id of the website scraper
- `location_id` is the id of the office/calendar available on the website
  - Both `source_id` and `location_id` together identify the unique calendar
    within the dataset. The actual names can be looked up in the [meta-data](#metadata).
- All other columns represent the availability of each date.
  - The spacing between dates is 5 to 30 minutes, depending on the website.
  - For space reasons, dates that are not available just have an empty value, 
    available dates contain a `1`. 
  - Usually the free dates columns show the upcoming 4 weeks from the point of
    the snapshot date.

The actual data is quite redundant and gigantic in size but the zipped weekly
bundles are currently between 6 to 8 megabytes each.


# Metadata

[metadata.json](compressed/metadata.json) contains an object in the 
following format:

```json
{
  "*source_id*": {
    "name": "full name of source/website",
    "url": "url of website",
    "locations": {
      "*location_id*": {
        "name": "name of office/building",
        "services": [
          "things you can do there"
        ]    
      }
    } 
  }
}
```

`source_id` and `location_id` can be looked up via:

`location_info = metadata[source_id]["locations"][location_id]`


# Data access

[data.py](data.py) defines a `Data` class that helps to iterate through all
the files in the dataset:

```python
from data import Data

data = Data()  # filters can be defined here

# iterate through all files
# week: tuple(year, week)
# source_id: str
# fileio: binary stream
for week, source_id, fileio in data.iter_files():
    pass

# iterate through the table data
# columns: list of headers, e.g ["date", "source_id", "location_id", "2021-07-12 08:00:00", ...]
# rows: list of list of values
for week, source_id, columns, rows in data.iter_tables(as_int=True):
    pass

# iterate through pandas.DataFrames
# df: a DataFrame with MultiIndex ["date", "source_id", "location_id"]
for week, source_id, df in data.iter_dataframes():
    pass
```

Meta-data can be queried via:

```python
# returns the plain dict
data.meta   

# returns a value for the given source_id 
#   get_meta() does not raise KeyError, but returns the `default` value 
data.get_meta("source_id", "value")  

# returns a value for the given source_id/location_id
data.get_meta("source_id", "location_id", "value")  
```

# Metrics

Metrics have been updated at **%(metrics_date)s**

**%(num_sources)s** sources,
**%(num_locations)s** locations,
**%(num_snapshots)s** snapshots,
**%(num_appointments)s** estimated appointments

- [snapshots-sum.csv](metrics/snapshots-sum.csv) (below table) contains
  the sum of all weeks per **source**. 
- [snapshots-weekly.csv](metrics/snapshots-weekly.csv) contains the number of 
  snapshots and changes per **calendar week** and **source**.

%(metric_sum_table)s

Where the columns are:

 - `source_id`, `name`, `scraper`: 
   The source of the scraped data. 
   See [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/)
   for details.
 - `num_locations`: The average number of locations or different offices
   that are found for the source.
 - `num_snapshots`: The number of successful snapshots of the website data.
 - `num_changes`: The number of changes in the schedule data, summed over all
   locations. That means, whenever a location shows a different schedule
   compared to the previous snapshot, the number is increased by 1. 
 - `num_appointments`: The **estimated** number of appointments that have been 
   made, summed over all locations. Please read below note!
 - `num_cancellations`: Similar to `num_appointments` but this shows the
   number of free dates that have reappeared on the schedule. 

The [snapshots-weekly.csv](metrics/snapshots-weekly.csv) table is similar
but contains a row for each calendar week as well. 

> There are some problems estimating the actual number of appointments
> and cancellations. Including strange data from the websites at some
> points in time. In the above tables, the numbers for appointments
> and cancellations are summed over the estimated numbers 
> per snapshot, limited to 1. That means that no location can contribute
> more than 1 appointment/cancellation per 15 minutes. That mitigates one
> of the problems, where a sequence of free 5-minute slots disappears,
> probably because they are occupied by one longer appointment.

