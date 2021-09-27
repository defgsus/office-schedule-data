## History of free office appointment dates (in Germany)

This is the data export of [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/).

The data contains the **free dates** where one can make an appointment at a 
public office at a snapshot interval of 15 minutes, starting on 2021-07-12.

This data repository is updated weekly and the most recent timestamp 
is **2021-09-26 23:52:49**.


# Data layout

The [raw/](raw) folder contains **tar.gz** files for each 
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
    within the dataset. The actual names can be looked up in the [meta data](#meta-data).
- All other columns represent the availability of each date.
  - The spacing between dates is 5 to 30 minutes, depending on the website.
  - For space reasons, dates that are not available just have an empty value, 
    available dates contain a `1`. 
  - Usually the free dates columns show the upcoming 4 weeks from the point of
    the snapshot date.

The actual data is quite redundant and gigantic in size but the zipped weekly
bundles are currently between 6 to 8 megabytes each.


# Data access

For a pythonian way read the [data access documentation](docs/data_access.md).


## Meta data

Some metadata is found in [raw/metadata.json](raw/metadata.json) 
and contains an object of the following format:

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

Within python, it can be queried via:

```python
from src.data import Data

# returns the plain dict
Data.meta()

# returns a value (e.g. "name") for the given source_id 
#   get_meta() does not raise KeyError, but returns the `default` value 
Data.get_meta("source_id", "value")  

# returns a value (e.g. "name") for the given source_id/location_id
Data.get_meta("source_id", "location_id", "value")  
```

# Metrics

Metrics have been updated at **2021-09-27**

**98** sources,
**575** locations,
**486,943** snapshots,
**293,002** estimated appointments

- [summary.csv](metrics/summary.csv) (below table) contains
  the sum of all weeks per **source**. 
- [summary-weekly.csv](metrics/summary-weekly.csv) contains the number of 
  snapshots and changes per **calendar week** and **source**.

| source_id                                                                                                           |   num_locations |   num_snapshots |   num_changes |   num_appointments |   num_cancellations | min_date            | max_date            | scraper    | name                                                   |
|:--------------------------------------------------------------------------------------------------------------------|----------------:|----------------:|--------------:|-------------------:|--------------------:|:--------------------|:--------------------|:-----------|:-------------------------------------------------------|
| [amberg](https://termine.amberg.de)                                                                                 |               4 |            6044 |          2265 |               1387 |                 185 | 2021-07-26 00:03:02 | 2021-09-26 23:48:04 | tevis      | Stadt Amberg                                           |
| [badkreuznach](https://termine-reservieren.de/termine/svkh)                                                         |               4 |            6028 |          3568 |               1705 |                 599 | 2021-07-26 00:03:10 | 2021-09-26 23:48:11 | tevis      | Stadt Bad-Kreuznach                                    |
| [bbmess](https://www.etermin.net/lme-be-bb)                                                                         |               2 |            3865 |           474 |                256 |                  51 | 2021-07-26 00:03:02 | 2021-09-26 03:18:04 | etermin    | Landesamt für Mess- und Eichwesen Berlin-Brandenburg   |
| [bernkastelwittlich](https://termine-reservieren.de/termine/bernkastel-wittlich)                                    |               3 |            6037 |          3965 |               2625 |                1345 | 2021-07-26 00:03:17 | 2021-09-26 23:48:16 | tevis      | Landkreis Bernkastel-Wittlich                          |
| [billerbeck](https://www.etermin.net/termininbillerbeck)                                                            |               3 |            6047 |          1150 |                757 |                  91 | 2021-07-26 00:03:04 | 2021-09-26 23:48:07 | etermin    | Stadt Billerbeck Verwaltung                            |
| [blankenburg](https://www.etermin.net/blankenburg)                                                                  |               2 |            6047 |           841 |                674 |                  35 | 2021-07-26 00:03:04 | 2021-09-26 23:48:07 | etermin    | Stadt Blankenburg (Harz)                               |
| [bonn](https://onlinetermine.bonn.de/index.php?company=stadtbonn)                                                   |               3 |            7385 |          8338 |               6626 |                2772 | 2021-07-12 00:03:33 | 2021-09-26 23:48:26 | netappoint | Stadt Bonn                                             |
| [bonnbau](https://onlinetermine.bonn.de/index.php?company=stadtbonn-bau)                                            |               1 |            7385 |           500 |                 44 |                   2 | 2021-07-12 00:03:38 | 2021-09-26 23:48:03 | netappoint | Stadt Bonn Bauamt                                      |
| [bonnjob](https://www.etermin.net/jcbn)                                                                             |               4 |            6047 |          1441 |                 62 |                 393 | 2021-07-26 00:03:05 | 2021-09-26 23:48:08 | etermin    | Jobcenter Bonn                                         |
| [braunschweigtest](https://www.etermin.net/coronatestbs)                                                            |               1 |             637 |            59 |                 20 |                   1 | 2021-07-26 00:03:05 | 2021-08-01 15:03:18 | etermin    | Corona Test Braunschweig                               |
| [burgendlandkaa](https://www.etermin.net/GBRBgld)                                                                   |               1 |            6047 |           134 |                  5 |                   0 | 2021-07-26 00:03:06 | 2021-09-26 23:48:08 | etermin    | Kammer für Arbeiter und Angestellte für das Burgenland |
| [butzbach](https://www.etermin.net/stadtbutzbach)                                                                   |               2 |            6047 |          1088 |                646 |                  92 | 2021-07-26 00:03:06 | 2021-09-26 23:48:09 | etermin    | Magistrat der Stadt Butzbach                           |
| [cochemzell](https://termine-reservieren.de/termine/cochem-zell)                                                    |               6 |            6039 |          3666 |               1057 |                 412 | 2021-07-26 00:03:27 | 2021-09-26 23:48:25 | tevis      | Landkreis Cochem-Zell                                  |
| [coesfeld](https://www.etermin.net/coe)                                                                             |               2 |            6048 |           754 |                104 |                  23 | 2021-07-26 00:03:07 | 2021-09-26 23:48:09 | etermin    | Stadt Coesfeld                                         |
| [daunvg](https://www.etermin.net/vgdaun)                                                                            |               1 |            5345 |           326 |                205 |                  17 | 2021-07-26 00:03:07 | 2021-09-26 23:48:10 | etermin    | Verbandsgemeindeverwaltung Daun                        |
| [dormagen](https://www.etermin.net/stadtdormagen)                                                                   |               2 |            1292 |           305 |                143 |                   4 | 2021-07-26 08:18:09 | 2021-09-24 12:48:09 | etermin    | Stadt Dormagen                                         |
| [dresden](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-fs)                                  |               3 |            7382 |          1881 |               1105 |                 516 | 2021-07-12 00:03:49 | 2021-09-26 23:48:10 | netappoint | Stadt Dresden                                          |
| [dresdenkfz](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-kfz)                              |               4 |            7384 |          6405 |               4031 |                1333 | 2021-07-12 00:04:05 | 2021-09-26 23:48:11 | netappoint | Stadt Dresden Kfz-Zulassungsbehörde                    |
| [duelmen](https://www.etermin.net/duelmen)                                                                          |               8 |            6046 |          4696 |               2967 |                 569 | 2021-07-26 00:03:22 | 2021-09-26 23:48:19 | etermin    | Stadt Dülmen                                           |
| [egelsbach](https://tevis.ekom21.de/egb)                                                                            |               3 |            3503 |           575 |                 80 |                  37 | 2021-07-12 00:04:06 | 2021-08-17 14:33:04 | tevis      | Stadt Egelsbach                                        |
| [eislingen](https://termine-reservieren.de/termine/eislingen)                                                       |              16 |            6025 |          4812 |                712 |                 973 | 2021-07-26 00:03:50 | 2021-09-26 23:48:52 | tevis      | Stadt Eislingen                                        |
| [elitheratest](https://www.etermin.net/testzentrum1)                                                                |               1 |             458 |            47 |                 10 |                   9 | 2021-07-26 00:03:22 | 2021-07-31 10:03:50 | etermin    | Corona TESTZENTRUM im Elithera                         |
| [frankenthal](https://termine-reservieren.de/termine/frankenthal)                                                   |               4 |            6031 |          2221 |               1316 |                 622 | 2021-07-26 00:03:57 | 2021-09-26 23:48:58 | tevis      | Stadt Frankenthal                                      |
| [frankfurt](https://tevis.ekom21.de/fra)                                                                            |              15 |            3507 |          9012 |               3608 |                2897 | 2021-07-12 00:04:11 | 2021-08-17 14:33:14 | tevis      | Stadt Frankfurt                                        |
| [friedrichsdorf](https://tevis.ekom21.de/frf)                                                                       |              11 |            3507 |          2509 |                462 |                 129 | 2021-07-12 00:04:13 | 2021-08-17 14:33:19 | tevis      | Stadt Friedrichsdorf                                   |
| [fuerthtest](https://www.etermin.net/Testzentrum_agnf)                                                              |               1 |            6048 |          2121 |                486 |                 449 | 2021-07-26 00:03:22 | 2021-09-26 23:48:19 | etermin    | SARS-CoV-2 Testzentrum der Stadt Fürth                 |
| [geldernsw](https://www.etermin.net/Zaehlerwechseltermine)                                                          |               1 |            6047 |          1506 |               1335 |                   0 | 2021-07-26 00:03:23 | 2021-09-26 23:48:20 | etermin    | Stadtwerke Geldern Netz                                |
| [goslartest](https://www.etermin.net/testzentrumgoslar)                                                             |               1 |            6047 |          2264 |               1786 |                 287 | 2021-07-26 00:03:24 | 2021-09-26 23:48:21 | etermin    | Testzentrum Goslar                                     |
| [graz](https://www.etermin.net/stadtgraz)                                                                           |              39 |            6037 |         33187 |              15528 |                2941 | 2021-07-26 00:03:48 | 2021-09-26 23:48:47 | etermin    | Stadt Graz                                             |
| [grazamt](https://www.etermin.net/buergerinnenamt)                                                                  |               9 |            6044 |          5255 |               2489 |                 900 | 2021-07-26 00:03:53 | 2021-09-26 23:48:48 | etermin    | BürgerInnenamt Stadt Graz                              |
| [grazuni](https://www.etermin.net/unitestet)                                                                        |               1 |            4407 |           519 |                  1 |                   0 | 2021-08-12 02:19:47 | 2021-09-26 23:48:49 | etermin    | Universität Graz                                       |
| [gronau](https://termine-reservieren.de/termine/gronau)                                                             |               7 |            6031 |          2569 |               1172 |                 449 | 2021-07-26 00:04:01 | 2021-09-26 23:49:13 | tevis      | Stadt Gronau                                           |
| [grossumstadt](https://tevis.ekom21.de/gad)                                                                         |               3 |            3508 |          1471 |                550 |                 198 | 2021-07-12 00:04:14 | 2021-08-17 14:33:21 | tevis      | Stadt Groß-Umstadt                                     |
| [halbersadt](https://www.etermin.net/halberstadt)                                                                   |               2 |            6047 |           284 |                117 |                   5 | 2021-07-26 00:03:54 | 2021-09-26 23:48:50 | etermin    | Stadt Halberstadt                                      |
| [halle](https://ncu.halle.de/index.php?company=stadthalle)                                                          |              22 |            6048 |          9429 |               5958 |                2362 | 2021-07-26 00:03:31 | 2021-09-26 23:48:27 | netappoint | Stadt Halle                                            |
| [hammersbachtest](https://www.etermin.net/Schnelltestzentrum)                                                       |               3 |            6048 |          6876 |               3521 |                 289 | 2021-07-26 00:03:55 | 2021-09-26 23:48:51 | etermin    | Schnelltestzentrum Hammersbach                         |
| [heidelberg](https://tevis-online.heidelberg.de)                                                                    |               8 |            7387 |          6519 |               2758 |                1548 | 2021-07-12 00:04:15 | 2021-09-26 23:48:04 | tevis      | Stadt Heidelberg                                       |
| [hersfeldtest](https://www.etermin.net/testcenter-hef-rof)                                                          |               1 |            6048 |          1189 |                508 |                 340 | 2021-07-26 00:03:56 | 2021-09-26 23:48:51 | etermin    | Corona-Testcenter Hersfeld-Rotenburg                   |
| [hof](https://termine-reservieren.de/termine/hof)                                                                   |               3 |            6030 |          2412 |               1530 |                 383 | 2021-07-26 00:04:07 | 2021-09-26 23:49:18 | tevis      | Stadt Hof                                              |
| [hornberg](https://tevis.ekom21.de/hbe)                                                                             |               1 |            3508 |           543 |                193 |                  95 | 2021-07-12 00:04:16 | 2021-08-17 14:33:21 | tevis      | Stadt Hornberg                                         |
| [hsktest](https://www.etermin.net/hsk-schnelltest)                                                                  |               1 |            6048 |          1310 |                173 |                  67 | 2021-07-26 00:03:57 | 2021-09-26 23:48:52 | etermin    | Hochsauerlandkreis                                     |
| [huenstetten](https://tevis.ekom21.de/hsz)                                                                          |               4 |            3508 |           675 |                233 |                  61 | 2021-07-12 00:04:17 | 2021-08-17 14:33:24 | tevis      | Stadt Hünstetten                                       |
| [huettenberg](https://tevis.ekom21.de/htb)                                                                          |               9 |            3508 |           851 |                112 |                  35 | 2021-07-12 00:04:21 | 2021-08-17 14:33:30 | tevis      | Stadt Hüttenberg                                       |
| [ilmkreis](https://tvweb.ilm-kreis.de/ilmkreis)                                                                     |               1 |            7136 |             0 |                  0 |                   0 | 2021-07-12 00:04:22 | 2021-09-26 23:48:02 | tevis      | Ilm-Kreis                                              |
| [impfthueringen](https://www.impfen-thueringen.de/terminvergabe)                                                    |              74 |            7385 |        255191 |             145780 |              164953 | 2021-07-12 00:00:00 | 2021-09-26 23:45:00 | custom     | Impftermin Thüringen                                   |
| [ingelheim](https://termine-reservieren.de/termine/ingelheim)                                                       |               1 |            6040 |          1290 |                591 |                 412 | 2021-07-26 00:04:09 | 2021-09-26 23:49:21 | tevis      | Stadt Ingelheim                                        |
| [innsbruckpsych](https://www.etermin.net/PSB-Innsbruck)                                                             |               1 |            1045 |            15 |                  2 |                   1 | 2021-07-26 00:03:57 | 2021-09-24 08:49:02 | etermin    | Psychologische Studierendenberatung Innsbruck          |
| [itzehoe](https://www.etermin.net/Stadt_Itzehoe)                                                                    |               3 |            2650 |           421 |                224 |                  21 | 2021-07-26 15:19:04 | 2021-09-26 13:48:56 | etermin    | Stadt Itzehoe Einwohnermeldeamt                        |
| [jena](https://tevis-bs.jena.de)                                                                                    |               6 |            7383 |          9644 |               6314 |                3080 | 2021-07-12 00:04:23 | 2021-09-26 23:48:03 | tevis      | Stadt Jena                                             |
| [kaiserslauternausl](https://www3.kaiserslautern.de/netappoint/index.php?company=kaiserslautern-ausl)               |               2 |            7387 |             0 |                  0 |                   0 | 2021-07-12 00:04:24 | 2021-09-26 23:48:01 | netappoint | Stadt Kaiserslautern Ausländerbehörde                  |
| [kassel](https://tevis.ekom21.de/kas)                                                                               |              14 |            3508 |          7544 |               4065 |                1804 | 2021-07-12 00:04:29 | 2021-08-17 14:33:36 | tevis      | Stadt Kassel                                           |
| [kelsterbach](https://tevis.ekom21.de/keb)                                                                          |               1 |            3508 |           575 |                114 |                  61 | 2021-07-12 00:04:30 | 2021-08-17 14:33:37 | tevis      | Stadt Kelsterbach                                      |
| [kreisbergstrasse](https://terminreservierungverkehr.kreis-bergstrasse.de/netappoint/index.php?company=bergstrasse) |               2 |            7189 |          3568 |               2108 |                 957 | 2021-07-12 00:04:53 | 2021-09-26 23:48:09 | netappoint | Kreis Bergstraße                                       |
| [kreisgermersheimkfz](https://kfz.kreis-germersheim.de/netappoint/index.php?company=kreis-germersheim)              |               1 |            7383 |           640 |                324 |                 108 | 2021-07-12 00:04:55 | 2021-09-26 23:48:01 | netappoint | Kreis Germersheim Kfz-Zulassungsbehörde                |
| [kreisgrossgerau](https://tevis.ekom21.de/grg)                                                                      |              12 |            3321 |          4437 |               1138 |                 917 | 2021-07-12 00:04:59 | 2021-08-17 13:48:44 | tevis      | Kreis Groß-Gerau                                       |
| [kreissteinfurt](https://www.etermin.net/kreis-steinfurt)                                                           |               1 |            1577 |           260 |                181 |                  15 | 2021-07-26 00:03:58 | 2021-08-11 10:05:11 | etermin    | Kreis Steinfurt                                        |
| [kreiswesel](https://tevis.krzn.de/tevisweb080)                                                                     |               4 |            7378 |         11434 |               7529 |                5455 | 2021-07-12 00:05:02 | 2021-09-26 23:48:03 | tevis      | Kreis Wesel                                            |
| [kvmayenkoblenz](https://termine-reservieren.de/termine/kvmayen-koblenz)                                            |               5 |            6033 |          5262 |               2672 |                1433 | 2021-07-26 00:04:22 | 2021-09-26 23:49:30 | tevis      | Landkreis Mayen-Koblenz                                |
| [lehrte](https://www.etermin.net/StadtLehrte)                                                                       |               7 |            6048 |          4393 |               3225 |                 579 | 2021-07-26 00:04:06 | 2021-09-26 23:49:00 | etermin    | Stadt Lehrte                                           |
| [leipzig](https://leipzig.de/fachanwendungen/termine/index.html)                                                    |              22 |            6046 |         13993 |              10005 |                1463 | 2021-07-26 00:03:13 | 2021-09-26 23:48:15 | custom     | Stadt Leipzig                                          |
| [leipzigstandesamt](https://adressen.leipzig.de/netappoint/index.php?company=leipzig-standesamt)                    |               3 |            7388 |           955 |                535 |                 189 | 2021-07-12 00:05:04 | 2021-09-26 23:48:04 | netappoint | Stadt Leipzig Standesamt                               |
| [leun](https://tevis.ekom21.de/lnx)                                                                                 |               6 |            1590 |           592 |                 56 |                  11 | 2021-07-12 00:05:05 | 2021-08-17 00:22:10 | tevis      | Stadt Leun                                             |
| [linsengericht](https://tevis.ekom21.de/lsg)                                                                        |               1 |            1461 |           220 |                 34 |                  18 | 2021-07-12 00:05:05 | 2021-08-17 00:22:11 | tevis      | Stadt Linsengericht                                    |
| [loehne](https://termine-reservieren.de/termine/loehne)                                                             |              21 |            6024 |          7544 |                984 |                 187 | 2021-07-26 00:04:53 | 2021-09-26 23:50:03 | tevis      | Stadt Löhne                                            |
| [lramiesbach](https://termine-reservieren.de/termine/lra-miesbach)                                                  |               3 |            6033 |          2861 |               1679 |                 993 | 2021-07-26 00:04:57 | 2021-09-26 23:50:11 | tevis      | Landratsamt Miesbach                                   |
| [lramuenchenefa](https://termine-reservieren.de/termine/lramuenchen/efa)                                            |               4 |            6030 |          2036 |                745 |                 250 | 2021-07-26 00:05:01 | 2021-09-26 23:50:34 | tevis      | Landratsamt München                                    |
| [magdeburg](https://service.magdeburg.de/netappoint/index.php?company=magdeburg)                                    |              27 |            7038 |          8128 |               1088 |                 293 | 2021-07-12 00:05:32 | 2021-09-26 23:48:08 | netappoint | Stadt Magdeburg                                        |
| [mainz](https://otv.mainz.de)                                                                                       |              16 |            6021 |         12657 |               8676 |                2618 | 2021-07-26 00:03:22 | 2021-09-26 23:48:21 | tevis      | Stadt Mainz                                            |
| [minden](https://termine-reservieren.de/termine/minden)                                                             |               3 |            6034 |          5000 |               3331 |                1308 | 2021-07-26 00:05:06 | 2021-09-26 23:50:39 | tevis      | Stadt Minden                                           |
| [mittenwalde](https://www.etermin.net/StadtMittenwalde)                                                             |               3 |            6048 |           726 |                 67 |                   7 | 2021-07-26 00:04:06 | 2021-09-26 23:49:00 | etermin    | Stadt Mittenwalde                                      |
| [moerlenbach](https://tevis.ekom21.de/mah)                                                                          |               1 |            1375 |           257 |                 20 |                   9 | 2021-07-12 00:05:32 | 2021-08-17 00:22:12 | tevis      | Stadt Mörlenbach                                       |
| [neuisenburg](https://tevis.ekom21.de/nis)                                                                          |               1 |            1334 |           238 |                 24 |                  22 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 | tevis      | Stadt Neu-Isenburg                                     |
| [niedenstein](https://tevis.ekom21.de/nsn)                                                                          |               1 |            1294 |           204 |                 17 |                   4 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 | tevis      | Stadt Niedenstein                                      |
| [nordhausen](https://tevis.svndh.de)                                                                                |               2 |            7313 |          2114 |               1201 |                 702 | 2021-07-12 00:05:35 | 2021-09-26 23:48:04 | tevis      | Stadt Nordhausen                                       |
| [oberasbach](https://www.etermin.net/stadtoberasbach)                                                               |               1 |             633 |            38 |                 10 |                   2 | 2021-07-26 11:04:16 | 2021-09-19 17:04:43 | etermin    | Stadt Oberasbach                                       |
| [oberramstadt](https://tevis.ekom21.de/oby)                                                                         |               6 |            1196 |          1191 |                140 |                 117 | 2021-07-12 00:05:38 | 2021-08-17 00:22:17 | tevis      | Stadt Ober-Ramstadt                                    |
| [oesterreichgk](https://www.etermin.net/OEGK)                                                                       |               4 |            2397 |             0 |                  0 |                   0 | 2021-09-02 00:06:35 | 2021-09-26 23:49:33 | etermin    | Österreichische Gesundheitskasse                       |
| [offenbach](https://tevis.ekom21.de/off)                                                                            |               9 |            1185 |          1522 |                 23 |                   3 | 2021-07-12 00:05:41 | 2021-08-17 00:22:22 | tevis      | Stadt Offenbach                                        |
| [olfen](https://www.etermin.net/stadtolfen)                                                                         |               1 |            6047 |          1057 |                495 |                  56 | 2021-07-26 00:04:18 | 2021-09-26 23:49:33 | etermin    | Stadt Olfen                                            |
| [paderborn](https://termine-reservieren.de/termine/paderborn)                                                       |              16 |            6028 |         13627 |               6018 |                4197 | 2021-07-26 00:05:36 | 2021-09-26 23:51:10 | tevis      | Stadt Paderborn                                        |
| [pfungstadt](https://tevis.ekom21.de/pft)                                                                           |               2 |            1170 |           520 |                 89 |                  55 | 2021-07-12 00:05:43 | 2021-08-13 23:34:33 | tevis      | Stadt Pfungstadt                                       |
| [salzgitter](https://termine-reservieren.de/termine/salzgitter)                                                     |              26 |            6026 |          7807 |               3066 |                1247 | 2021-07-26 00:06:21 | 2021-09-26 23:51:58 | tevis      | Stadt Salzgitter                                       |
| [schoenebeckelbe](https://termine-reservieren.de/termine/schoenebeck-elbe)                                          |               1 |            6036 |           387 |                195 |                  76 | 2021-07-26 00:06:23 | 2021-09-26 23:52:00 | tevis      | Stadt Schönebeck (Elbe)                                |
| [selm](https://www.etermin.net/stadtselm)                                                                           |               2 |            1833 |            88 |                 43 |                   2 | 2021-07-26 09:49:51 | 2021-09-24 09:19:40 | etermin    | Stadt Selm                                             |
| [speyer](https://termine-reservieren.de/termine/speyer)                                                             |               6 |            6035 |          1540 |                857 |                 214 | 2021-07-26 00:06:26 | 2021-09-26 23:52:04 | tevis      | Stadt Speyer                                           |
| [stadtbergen](https://www.etermin.net/stadtbergen)                                                                  |               2 |            5760 |           776 |                232 |                 262 | 2021-07-26 00:04:20 | 2021-09-26 18:34:33 | etermin    | Stadt Stadtbergen                                      |
| [stadtsoest](https://termine-reservieren.de/termine/stadtsoest)                                                     |               1 |            6037 |          2000 |               1387 |                 852 | 2021-07-26 00:06:28 | 2021-09-26 23:52:07 | tevis      | Stadt Söst                                             |
| [steinburg](https://termine-reservieren.de/termine/steinburg)                                                       |               2 |            6036 |           209 |                  7 |                   3 | 2021-07-26 00:06:32 | 2021-09-26 23:52:11 | tevis      | Stadt Steinburg                                        |
| [teublitztest](https://www.etermin.net/spitzwegapo)                                                                 |               1 |            6048 |          1218 |                703 |                 285 | 2021-07-26 00:04:21 | 2021-09-26 23:49:35 | etermin    | Corona-Schnellteststelle Teublitz                      |
| [trier](https://termine-reservieren.de/termine/trier)                                                               |               5 |            6028 |          2330 |               1014 |                 410 | 2021-07-26 00:06:43 | 2021-09-26 23:52:23 | tevis      | Stadt Trier                                            |
| [unna](https://termine-reservieren.de/termine/unna)                                                                 |               2 |            6034 |          1763 |               1037 |                 668 | 2021-07-26 00:06:46 | 2021-09-26 23:52:27 | tevis      | Stadt Unna                                             |
| [viernheim](https://tevis.ekom21.de/vhx)                                                                            |               1 |            1169 |           315 |                 52 |                  31 | 2021-07-12 00:05:43 | 2021-08-13 23:34:34 | tevis      | Stadt Viernheim                                        |
| [weilheimschongau](https://termine-reservieren.de/termine/weilheimschongau)                                         |               2 |            6032 |           869 |                392 |                 128 | 2021-07-26 00:06:51 | 2021-09-26 23:52:30 | tevis      | Landkreis Weilheim-Schongau                            |
| [weimar](https://tevis.weimar.de)                                                                                   |               1 |            7383 |          2216 |                961 |                 809 | 2021-07-12 00:05:44 | 2021-09-26 23:48:02 | tevis      | Stadt Weimar                                           |
| [weiterstadt](https://tevis.ekom21.de/wdt)                                                                          |               2 |            1135 |           581 |                 51 |                  19 | 2021-07-12 00:05:45 | 2021-08-09 15:34:56 | tevis      | Stadt Weiterstadt                                      |
| [wiehl](https://www.etermin.net/stadtwiehl)                                                                         |               1 |             107 |             5 |                  0 |                   0 | 2021-07-27 09:34:23 | 2021-09-07 10:36:52 | etermin    | Stadt Wiehl                                            |
| [wittmund](https://termine-reservieren.de/termine/wittmund/stva)                                                    |               3 |            6027 |          1796 |                721 |                 439 | 2021-07-26 00:06:56 | 2021-09-26 23:52:36 | tevis      | Stadt Wittmund                                         |
| [worms](https://termine-reservieren.de/termine/worms)                                                               |               7 |            6029 |          5739 |               3723 |                1986 | 2021-07-26 00:07:06 | 2021-09-26 23:52:49 | tevis      | Stadt Worms                                            |

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

The [summary-weekly.csv](metrics/summary-weekly.csv) table is similar
but contains a row for each calendar week as well. 

> There are some problems estimating the actual number of appointments
> and cancellations. Including strange data from the websites at some
> points in time. In the above tables, the numbers for appointments
> and cancellations are summed over the estimated numbers 
> per snapshot, limited to 1. That means that no location can contribute
> more than 1 appointment/cancellation per 15 minutes. That mitigates one
> of the problems, where a sequence of free 5-minute slots disappears,
> probably because they are occupied by one longer appointment.

