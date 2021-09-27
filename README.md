## History of free office appointment dates (in Germany)

This is the data export of [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/).

The data contains the **free dates** where one can make an appointment at a 
public office at a snapshot interval of 15 minutes, starting at 2021-07-12.

This repository is updated each week and the most recent timestamp 
is **2021-09-19**.


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

Metrics have been updated at **2021-09-22**

**98** sources,
**575** locations,
**441,160** snapshots,
**261,133** estimated appointments

- [snapshots-sum.csv](metrics/snapshots-sum.csv) (below table) contains
  the sum of all weeks per **source**. 
- [snapshots-weekly.csv](metrics/snapshots-weekly.csv) contains the number of 
  snapshots and changes per **calendar week** and **source**.

| source_id                                                                                                           | name                                                   | scraper    |   num_locations |   num_snapshots |   num_changes |   num_appointments |   num_cancellations | min_date            | max_date            |
|:--------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|:-----------|----------------:|----------------:|--------------:|-------------------:|--------------------:|:--------------------|:--------------------|
| [amberg](https://termine.amberg.de)                                                                                 | Stadt Amberg                                           | tevis      |               4 |            5374 |          2010 |               1248 |                 119 | 2021-07-26 00:03:02 | 2021-09-19 23:48:04 |
| [badkreuznach](https://termine-reservieren.de/termine/svkh)                                                         | Stadt Bad-Kreuznach                                    | tevis      |               4 |            5356 |          3156 |               1500 |                 393 | 2021-07-26 00:03:10 | 2021-09-19 23:48:13 |
| [bbmess](https://www.etermin.net/lme-be-bb)                                                                         | Landesamt für Mess- und Eichwesen Berlin-Brandenburg   | etermin    |               2 |            3728 |           466 |                143 |                  39 | 2021-07-26 00:03:02 | 2021-09-17 08:33:04 |
| [bernkastelwittlich](https://termine-reservieren.de/termine/bernkastel-wittlich)                                    | Landkreis Bernkastel-Wittlich                          | tevis      |               3 |            5365 |          3537 |               2349 |                1095 | 2021-07-26 00:03:17 | 2021-09-19 23:48:17 |
| [billerbeck](https://www.etermin.net/termininbillerbeck)                                                            | Stadt Billerbeck Verwaltung                            | etermin    |               3 |            5376 |          1053 |                684 |                  62 | 2021-07-26 00:03:04 | 2021-09-19 23:48:09 |
| [blankenburg](https://www.etermin.net/blankenburg)                                                                  | Stadt Blankenburg (Harz)                               | etermin    |               2 |            5376 |           787 |                637 |                  17 | 2021-07-26 00:03:04 | 2021-09-19 23:48:10 |
| [bonn](https://onlinetermine.bonn.de/index.php?company=stadtbonn)                                                   | Stadt Bonn                                             | netappoint |               3 |            6713 |          7623 |               6018 |                2057 | 2021-07-12 00:03:33 | 2021-09-19 23:48:43 |
| [bonnbau](https://onlinetermine.bonn.de/index.php?company=stadtbonn-bau)                                            | Stadt Bonn Bauamt                                      | netappoint |               1 |            6713 |           455 |                 42 |                   2 | 2021-07-12 00:03:38 | 2021-09-19 23:48:06 |
| [bonnjob](https://www.etermin.net/jcbn)                                                                             | Jobcenter Bonn                                         | etermin    |               4 |            5376 |          1287 |                 34 |                 185 | 2021-07-26 00:03:05 | 2021-09-19 23:48:11 |
| [braunschweigtest](https://www.etermin.net/coronatestbs)                                                            | Corona Test Braunschweig                               | etermin    |               1 |             637 |            59 |                 20 |                   1 | 2021-07-26 00:03:05 | 2021-08-01 15:03:18 |
| [burgendlandkaa](https://www.etermin.net/GBRBgld)                                                                   | Kammer für Arbeiter und Angestellte für das Burgenland | etermin    |               1 |            5376 |           121 |                  5 |                   0 | 2021-07-26 00:03:06 | 2021-09-19 23:48:11 |
| [butzbach](https://www.etermin.net/stadtbutzbach)                                                                   | Magistrat der Stadt Butzbach                           | etermin    |               2 |            5376 |           989 |                517 |                  51 | 2021-07-26 00:03:06 | 2021-09-19 23:48:12 |
| [cochemzell](https://termine-reservieren.de/termine/cochem-zell)                                                    | Landkreis Cochem-Zell                                  | tevis      |               6 |            5367 |          3228 |                907 |                 284 | 2021-07-26 00:03:27 | 2021-09-19 23:48:28 |
| [coesfeld](https://www.etermin.net/coe)                                                                             | Stadt Coesfeld                                         | etermin    |               2 |            5376 |           679 |                 98 |                   7 | 2021-07-26 00:03:07 | 2021-09-19 23:48:13 |
| [daunvg](https://www.etermin.net/vgdaun)                                                                            | Verbandsgemeindeverwaltung Daun                        | etermin    |               1 |            4673 |           288 |                132 |                  11 | 2021-07-26 00:03:07 | 2021-09-19 23:48:14 |
| [dormagen](https://www.etermin.net/stadtdormagen)                                                                   | Stadt Dormagen                                         | etermin    |               2 |            1225 |           294 |                101 |                   3 | 2021-07-26 08:18:09 | 2021-09-14 13:48:13 |
| [dresden](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-fs)                                  | Stadt Dresden                                          | netappoint |               3 |            6711 |          1732 |               1020 |                 359 | 2021-07-12 00:03:49 | 2021-09-19 23:48:15 |
| [dresdenkfz](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-kfz)                              | Stadt Dresden Kfz-Zulassungsbehörde                    | netappoint |               4 |            6712 |          5837 |               3663 |                1058 | 2021-07-12 00:04:05 | 2021-09-19 23:48:17 |
| [duelmen](https://www.etermin.net/duelmen)                                                                          | Stadt Dülmen                                           | etermin    |               9 |            5374 |          4205 |               2624 |                 345 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 |
| [egelsbach](https://tevis.ekom21.de/egb)                                                                            | Stadt Egelsbach                                        | tevis      |               3 |            3503 |           575 |                 80 |                  12 | 2021-07-12 00:04:06 | 2021-08-17 14:33:04 |
| [eislingen](https://termine-reservieren.de/termine/eislingen)                                                       | Stadt Eislingen                                        | tevis      |              16 |            5355 |          4474 |                677 |                 958 | 2021-07-26 00:03:50 | 2021-09-19 23:48:52 |
| [elitheratest](https://www.etermin.net/testzentrum1)                                                                | Corona TESTZENTRUM im Elithera                         | etermin    |               1 |             458 |            47 |                 10 |                   9 | 2021-07-26 00:03:22 | 2021-07-31 10:03:50 |
| [frankenthal](https://termine-reservieren.de/termine/frankenthal)                                                   | Stadt Frankenthal                                      | tevis      |               4 |            5361 |          2013 |               1078 |                 451 | 2021-07-26 00:03:57 | 2021-09-19 23:49:00 |
| [frankfurt](https://tevis.ekom21.de/fra)                                                                            | Stadt Frankfurt                                        | tevis      |              15 |            3507 |          9012 |               3603 |                2485 | 2021-07-12 00:04:11 | 2021-08-17 14:33:14 |
| [friedrichsdorf](https://tevis.ekom21.de/frf)                                                                       | Stadt Friedrichsdorf                                   | tevis      |              11 |            3507 |          2509 |                461 |                 111 | 2021-07-12 00:04:13 | 2021-08-17 14:33:19 |
| [fuerthtest](https://www.etermin.net/Testzentrum_agnf)                                                              | SARS-CoV-2 Testzentrum der Stadt Fürth                 | etermin    |               1 |            5376 |          1922 |                456 |                 389 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 |
| [geldernsw](https://www.etermin.net/Zaehlerwechseltermine)                                                          | Stadtwerke Geldern Netz                                | etermin    |               2 |            5375 |          1339 |                  0 |                   0 | 2021-07-26 00:03:23 | 2021-09-19 23:48:31 |
| [goslartest](https://www.etermin.net/testzentrumgoslar)                                                             | Testzentrum Goslar                                     | etermin    |               1 |            5375 |          2026 |               1599 |                 216 | 2021-07-26 00:03:24 | 2021-09-19 23:48:32 |
| [graz](https://www.etermin.net/stadtgraz)                                                                           | Stadt Graz                                             | etermin    |              39 |            5366 |         29446 |              13255 |                2094 | 2021-07-26 00:03:48 | 2021-09-19 23:49:25 |
| [grazamt](https://www.etermin.net/buergerinnenamt)                                                                  | BürgerInnenamt Stadt Graz                              | etermin    |               9 |            5373 |          4866 |               2204 |                 386 | 2021-07-26 00:03:53 | 2021-09-19 23:49:26 |
| [grazuni](https://www.etermin.net/unitestet)                                                                        | Universität Graz                                       | etermin    |               1 |            3735 |           439 |                  1 |                   0 | 2021-08-12 02:19:47 | 2021-09-19 23:49:28 |
| [gronau](https://termine-reservieren.de/termine/gronau)                                                             | Stadt Gronau                                           | tevis      |               7 |            5361 |          2241 |               1040 |                 301 | 2021-07-26 00:04:01 | 2021-09-19 23:49:15 |
| [grossumstadt](https://tevis.ekom21.de/gad)                                                                         | Stadt Groß-Umstadt                                     | tevis      |               3 |            3508 |          1471 |                550 |                 131 | 2021-07-12 00:04:14 | 2021-08-17 14:33:21 |
| [halbersadt](https://www.etermin.net/halberstadt)                                                                   | Stadt Halberstadt                                      | etermin    |               2 |            5375 |           253 |                 96 |                   4 | 2021-07-26 00:03:54 | 2021-09-19 23:49:29 |
| [halle](https://ncu.halle.de/index.php?company=stadthalle)                                                          | Stadt Halle                                            | netappoint |              22 |            5376 |          8334 |               5257 |                1636 | 2021-07-26 00:03:31 | 2021-09-19 23:48:31 |
| [hammersbachtest](https://www.etermin.net/Schnelltestzentrum)                                                       | Schnelltestzentrum Hammersbach                         | etermin    |               3 |            5376 |          6196 |               3204 |                 213 | 2021-07-26 00:03:55 | 2021-09-19 23:49:31 |
| [heidelberg](https://tevis-online.heidelberg.de)                                                                    | Stadt Heidelberg                                       | tevis      |               8 |            6715 |          5879 |               2406 |                1254 | 2021-07-12 00:04:15 | 2021-09-19 23:48:04 |
| [hersfeldtest](https://www.etermin.net/testcenter-hef-rof)                                                          | Corona-Testcenter Hersfeld-Rotenburg                   | etermin    |               1 |            5376 |          1100 |                480 |                 302 | 2021-07-26 00:03:56 | 2021-09-19 23:49:32 |
| [hof](https://termine-reservieren.de/termine/hof)                                                                   | Stadt Hof                                              | tevis      |               3 |            5359 |          2169 |               1407 |                 214 | 2021-07-26 00:04:07 | 2021-09-19 23:49:22 |
| [hornberg](https://tevis.ekom21.de/hbe)                                                                             | Stadt Hornberg                                         | tevis      |               1 |            3508 |           543 |                193 |                  86 | 2021-07-12 00:04:16 | 2021-08-17 14:33:21 |
| [hsktest](https://www.etermin.net/hsk-schnelltest)                                                                  | Hochsauerlandkreis                                     | etermin    |               1 |            5376 |          1168 |                168 |                  59 | 2021-07-26 00:03:57 | 2021-09-19 23:49:34 |
| [huenstetten](https://tevis.ekom21.de/hsz)                                                                          | Stadt Hünstetten                                       | tevis      |               4 |            3508 |           675 |                233 |                  42 | 2021-07-12 00:04:17 | 2021-08-17 14:33:24 |
| [huettenberg](https://tevis.ekom21.de/htb)                                                                          | Stadt Hüttenberg                                       | tevis      |               9 |            3508 |           851 |                112 |                  24 | 2021-07-12 00:04:21 | 2021-08-17 14:33:30 |
| [ilmkreis](https://tvweb.ilm-kreis.de/ilmkreis)                                                                     | Ilm-Kreis                                              | tevis      |               1 |            6464 |             0 |                  0 |                   0 | 2021-07-12 00:04:22 | 2021-09-19 23:48:02 |
| [impfthueringen](https://www.impfen-thueringen.de/terminvergabe)                                                    | Impftermin Thüringen                                   | custom     |              75 |            6713 |        235241 |             132738 |              150645 | 2021-07-12 00:00:00 | 2021-09-19 23:45:00 |
| [ingelheim](https://termine-reservieren.de/termine/ingelheim)                                                       | Stadt Ingelheim                                        | tevis      |               1 |            5369 |          1156 |                531 |                 251 | 2021-07-26 00:04:09 | 2021-09-19 23:49:24 |
| [innsbruckpsych](https://www.etermin.net/PSB-Innsbruck)                                                             | Psychologische Studierendenberatung Innsbruck          | etermin    |               1 |             984 |            15 |                  0 |                   0 | 2021-07-26 00:03:57 | 2021-09-04 09:51:16 |
| [itzehoe](https://www.etermin.net/Stadt_Itzehoe)                                                                    | Stadt Itzehoe Einwohnermeldeamt                        | etermin    |               3 |            2550 |           408 |                146 |                  12 | 2021-07-26 15:19:04 | 2021-09-19 20:04:34 |
| [jena](https://tevis-bs.jena.de)                                                                                    | Stadt Jena                                             | tevis      |               6 |            6712 |          8725 |               5135 |                2372 | 2021-07-12 00:04:23 | 2021-09-19 23:48:05 |
| [kaiserslauternausl](https://www3.kaiserslautern.de/netappoint/index.php?company=kaiserslautern-ausl)               | Stadt Kaiserslautern Ausländerbehörde                  | netappoint |               2 |            6715 |             0 |                  0 |                   0 | 2021-07-12 00:04:24 | 2021-09-19 23:48:02 |
| [kassel](https://tevis.ekom21.de/kas)                                                                               | Stadt Kassel                                           | tevis      |              14 |            3508 |          7544 |               3896 |                1579 | 2021-07-12 00:04:29 | 2021-08-17 14:33:36 |
| [kelsterbach](https://tevis.ekom21.de/keb)                                                                          | Stadt Kelsterbach                                      | tevis      |               1 |            3508 |           575 |                114 |                  37 | 2021-07-12 00:04:30 | 2021-08-17 14:33:37 |
| [kreisbergstrasse](https://terminreservierungverkehr.kreis-bergstrasse.de/netappoint/index.php?company=bergstrasse) | Kreis Bergstraße                                       | netappoint |               2 |            6520 |          3295 |               1957 |                 800 | 2021-07-12 00:04:53 | 2021-09-19 23:48:19 |
| [kreisgermersheimkfz](https://kfz.kreis-germersheim.de/netappoint/index.php?company=kreis-germersheim)              | Kreis Germersheim Kfz-Zulassungsbehörde                | netappoint |               1 |            6711 |           573 |                289 |                  55 | 2021-07-12 00:04:55 | 2021-09-19 23:48:03 |
| [kreisgrossgerau](https://tevis.ekom21.de/grg)                                                                      | Kreis Groß-Gerau                                       | tevis      |              12 |            3321 |          4437 |               1080 |                 843 | 2021-07-12 00:04:59 | 2021-08-17 13:48:44 |
| [kreissteinfurt](https://www.etermin.net/kreis-steinfurt)                                                           | Kreis Steinfurt                                        | etermin    |               1 |            1577 |           260 |                181 |                  11 | 2021-07-26 00:03:58 | 2021-08-11 10:05:11 |
| [kreiswesel](https://tevis.krzn.de/tevisweb080)                                                                     | Kreis Wesel                                            | tevis      |               4 |            6706 |         10411 |               6612 |                4242 | 2021-07-12 00:05:02 | 2021-09-19 23:48:04 |
| [kvmayenkoblenz](https://termine-reservieren.de/termine/kvmayen-koblenz)                                            | Landkreis Mayen-Koblenz                                | tevis      |               5 |            5362 |          4661 |               2376 |                 831 | 2021-07-26 00:04:22 | 2021-09-19 23:49:34 |
| [lehrte](https://www.etermin.net/StadtLehrte)                                                                       | Stadt Lehrte                                           | etermin    |               7 |            5376 |          4031 |               2983 |                 274 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 |
| [leipzig](https://leipzig.de/fachanwendungen/termine/index.html)                                                    | Stadt Leipzig                                          | custom     |              22 |            5374 |         12375 |               8825 |                 588 | 2021-07-26 00:03:13 | 2021-09-19 23:48:15 |
| [leipzigstandesamt](https://adressen.leipzig.de/netappoint/index.php?company=leipzig-standesamt)                    | Stadt Leipzig Standesamt                               | netappoint |               3 |            6716 |           866 |                483 |                 154 | 2021-07-12 00:05:04 | 2021-09-19 23:48:04 |
| [leun](https://tevis.ekom21.de/lnx)                                                                                 | Stadt Leun                                             | tevis      |               6 |            1590 |           592 |                 49 |                  11 | 2021-07-12 00:05:05 | 2021-08-17 00:22:10 |
| [linsengericht](https://tevis.ekom21.de/lsg)                                                                        | Stadt Linsengericht                                    | tevis      |               1 |            1461 |           220 |                 34 |                  16 | 2021-07-12 00:05:05 | 2021-08-17 00:22:11 |
| [loehne](https://termine-reservieren.de/termine/loehne)                                                             | Stadt Löhne                                            | tevis      |              22 |            5353 |          6724 |                675 |                 124 | 2021-07-26 00:04:53 | 2021-09-19 23:50:06 |
| [lramiesbach](https://termine-reservieren.de/termine/lra-miesbach)                                                  | Landratsamt Miesbach                                   | tevis      |               3 |            5362 |          2537 |               1431 |                 773 | 2021-07-26 00:04:57 | 2021-09-19 23:50:12 |
| [lramuenchenefa](https://termine-reservieren.de/termine/lramuenchen/efa)                                            | Landratsamt München                                    | tevis      |               3 |            5360 |          1132 |                387 |                 127 | 2021-07-26 00:05:01 | 2021-09-19 23:50:16 |
| [magdeburg](https://service.magdeburg.de/netappoint/index.php?company=magdeburg)                                    | Stadt Magdeburg                                        | netappoint |              27 |            6471 |          7662 |                783 |                 120 | 2021-07-12 00:05:32 | 2021-09-19 23:48:13 |
| [mainz](https://otv.mainz.de)                                                                                       | Stadt Mainz                                            | tevis      |              16 |            5349 |         11139 |               7288 |                1660 | 2021-07-26 00:03:22 | 2021-09-19 23:48:22 |
| [minden](https://termine-reservieren.de/termine/minden)                                                             | Stadt Minden                                           | tevis      |               3 |            5364 |          4451 |               2942 |                1038 | 2021-07-26 00:05:06 | 2021-09-19 23:50:21 |
| [mittenwalde](https://www.etermin.net/StadtMittenwalde)                                                             | Stadt Mittenwalde                                      | etermin    |               3 |            5376 |           640 |                 61 |                   2 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 |
| [moerlenbach](https://tevis.ekom21.de/mah)                                                                          | Stadt Mörlenbach                                       | tevis      |               1 |            1375 |           257 |                 15 |                   9 | 2021-07-12 00:05:32 | 2021-08-17 00:22:12 |
| [neuisenburg](https://tevis.ekom21.de/nis)                                                                          | Stadt Neu-Isenburg                                     | tevis      |               1 |            1334 |           238 |                 21 |                  21 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 |
| [niedenstein](https://tevis.ekom21.de/nsn)                                                                          | Stadt Niedenstein                                      | tevis      |               1 |            1294 |           204 |                 17 |                   4 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 |
| [nordhausen](https://tevis.svndh.de)                                                                                | Stadt Nordhausen                                       | tevis      |               2 |            6715 |          1970 |               1129 |                 510 | 2021-07-12 00:05:35 | 2021-09-19 23:48:04 |
| [oberasbach](https://www.etermin.net/stadtoberasbach)                                                               | Stadt Oberasbach                                       | etermin    |               1 |             633 |            38 |                  5 |                   1 | 2021-07-26 11:04:16 | 2021-09-19 17:04:43 |
| [oberramstadt](https://tevis.ekom21.de/oby)                                                                         | Stadt Ober-Ramstadt                                    | tevis      |               6 |            1196 |          1191 |                139 |                 117 | 2021-07-12 00:05:38 | 2021-08-17 00:22:17 |
| [oesterreichgk](https://www.etermin.net/OEGK)                                                                       | Österreichische Gesundheitskasse                       | etermin    |               3 |            1725 |             0 |                  0 |                   0 | 2021-09-02 00:06:35 | 2021-09-19 23:50:18 |
| [offenbach](https://tevis.ekom21.de/off)                                                                            | Stadt Offenbach                                        | tevis      |               9 |            1185 |          1522 |                 22 |                   3 | 2021-07-12 00:05:41 | 2021-08-17 00:22:22 |
| [olfen](https://www.etermin.net/stadtolfen)                                                                         | Stadt Olfen                                            | etermin    |               1 |            5375 |           930 |                441 |                  31 | 2021-07-26 00:04:18 | 2021-09-19 23:50:18 |
| [paderborn](https://termine-reservieren.de/termine/paderborn)                                                       | Stadt Paderborn                                        | tevis      |              15 |            5357 |         11977 |               5301 |                3214 | 2021-07-26 00:05:36 | 2021-09-19 23:50:53 |
| [pfungstadt](https://tevis.ekom21.de/pft)                                                                           | Stadt Pfungstadt                                       | tevis      |               2 |            1170 |           520 |                 89 |                  55 | 2021-07-12 00:05:43 | 2021-08-13 23:34:33 |
| [salzgitter](https://termine-reservieren.de/termine/salzgitter)                                                     | Stadt Salzgitter                                       | tevis      |              26 |            5355 |          6879 |               2680 |                 839 | 2021-07-26 00:06:21 | 2021-09-19 23:51:39 |
| [schoenebeckelbe](https://termine-reservieren.de/termine/schoenebeck-elbe)                                          | Stadt Schönebeck (Elbe)                                | tevis      |               1 |            5365 |           352 |                178 |                  62 | 2021-07-26 00:06:23 | 2021-09-19 23:51:41 |
| [selm](https://www.etermin.net/stadtselm)                                                                           | Stadt Selm                                             | etermin    |               2 |            1687 |            84 |                 21 |                   2 | 2021-07-26 09:49:51 | 2021-09-19 23:50:19 |
| [speyer](https://termine-reservieren.de/termine/speyer)                                                             | Stadt Speyer                                           | tevis      |               6 |            5364 |          1329 |                723 |                 129 | 2021-07-26 00:06:26 | 2021-09-19 23:51:45 |
| [stadtbergen](https://www.etermin.net/stadtbergen)                                                                  | Stadt Stadtbergen                                      | etermin    |               2 |            5292 |           683 |                127 |                 201 | 2021-07-26 00:04:20 | 2021-09-19 23:50:19 |
| [stadtsoest](https://termine-reservieren.de/termine/stadtsoest)                                                     | Stadt Söst                                             | tevis      |               1 |            5366 |          1813 |               1253 |                 713 | 2021-07-26 00:06:28 | 2021-09-19 23:51:48 |
| [steinburg](https://termine-reservieren.de/termine/steinburg)                                                       | Stadt Steinburg                                        | tevis      |               2 |            5365 |           182 |                  4 |                   3 | 2021-07-26 00:06:32 | 2021-09-19 23:51:52 |
| [teublitztest](https://www.etermin.net/spitzwegapo)                                                                 | Corona-Schnellteststelle Teublitz                      | etermin    |               1 |            5376 |          1098 |                642 |                 166 | 2021-07-26 00:04:21 | 2021-09-19 23:50:20 |
| [trier](https://termine-reservieren.de/termine/trier)                                                               | Stadt Trier                                            | tevis      |               5 |            5357 |          2048 |                877 |                 273 | 2021-07-26 00:06:43 | 2021-09-19 23:52:05 |
| [unna](https://termine-reservieren.de/termine/unna)                                                                 | Stadt Unna                                             | tevis      |               2 |            5363 |          1586 |                936 |                 380 | 2021-07-26 00:06:46 | 2021-09-19 23:52:08 |
| [viernheim](https://tevis.ekom21.de/vhx)                                                                            | Stadt Viernheim                                        | tevis      |               1 |            1169 |           315 |                 52 |                  31 | 2021-07-12 00:05:43 | 2021-08-13 23:34:34 |
| [weilheimschongau](https://termine-reservieren.de/termine/weilheimschongau)                                         | Landkreis Weilheim-Schongau                            | tevis      |               2 |            5361 |           738 |                315 |                  92 | 2021-07-26 00:06:51 | 2021-09-19 23:52:11 |
| [weimar](https://tevis.weimar.de)                                                                                   | Stadt Weimar                                           | tevis      |               1 |            6712 |          1994 |                861 |                 407 | 2021-07-12 00:05:44 | 2021-09-19 23:48:03 |
| [weiterstadt](https://tevis.ekom21.de/wdt)                                                                          | Stadt Weiterstadt                                      | tevis      |               2 |            1135 |           581 |                 50 |                  18 | 2021-07-12 00:05:45 | 2021-08-09 15:34:56 |
| [wiehl](https://www.etermin.net/stadtwiehl)                                                                         | Stadt Wiehl                                            | etermin    |               1 |             107 |             5 |                  0 |                   0 | 2021-07-27 09:34:23 | 2021-09-07 10:36:52 |
| [wittmund](https://termine-reservieren.de/termine/wittmund/stva)                                                    | Stadt Wittmund                                         | tevis      |               3 |            5356 |          1598 |                644 |                 343 | 2021-07-26 00:06:56 | 2021-09-19 23:52:16 |
| [worms](https://termine-reservieren.de/termine/worms)                                                               | Stadt Worms                                            | tevis      |               6 |            5358 |          5063 |               3283 |                1574 | 2021-07-26 00:07:06 | 2021-09-19 23:52:28 |

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

