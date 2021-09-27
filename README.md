## History of free office appointment dates (in Germany)

This is the data export of [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/).

The data contains the **free dates** where one can make an appointment at a 
public office at a snapshot interval of 15 minutes, starting on 2021-07-12.

This data repository is updated weekly and the most recent timestamp 
is **2021-09-19 23:52:28**.


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
**441,160** snapshots,
**265,591** estimated appointments

- [summary.csv](metrics/summary.csv) (below table) contains
  the sum of all weeks per **source**. 
- [summary-weekly.csv](metrics/summary-weekly.csv) contains the number of 
  snapshots and changes per **calendar week** and **source**.

| source_id                                                                                                           |   num_locations |   num_snapshots |   num_changes |   num_appointments |   num_cancellations | min_date            | max_date            | scraper    | name                                                   |
|:--------------------------------------------------------------------------------------------------------------------|----------------:|----------------:|--------------:|-------------------:|--------------------:|:--------------------|:--------------------|:-----------|:-------------------------------------------------------|
| [amberg](https://termine.amberg.de)                                                                                 |               4 |            5374 |          2010 |               1248 |                 175 | 2021-07-26 00:03:02 | 2021-09-19 23:48:04 | tevis      | Stadt Amberg                                           |
| [badkreuznach](https://termine-reservieren.de/termine/svkh)                                                         |               4 |            5356 |          3156 |               1501 |                 526 | 2021-07-26 00:03:10 | 2021-09-19 23:48:13 | tevis      | Stadt Bad-Kreuznach                                    |
| [bbmess](https://www.etermin.net/lme-be-bb)                                                                         |               2 |            3728 |           466 |                253 |                  51 | 2021-07-26 00:03:02 | 2021-09-17 08:33:04 | etermin    | Landesamt für Mess- und Eichwesen Berlin-Brandenburg   |
| [bernkastelwittlich](https://termine-reservieren.de/termine/bernkastel-wittlich)                                    |               3 |            5365 |          3537 |               2351 |                1196 | 2021-07-26 00:03:17 | 2021-09-19 23:48:17 | tevis      | Landkreis Bernkastel-Wittlich                          |
| [billerbeck](https://www.etermin.net/termininbillerbeck)                                                            |               3 |            5376 |          1053 |                685 |                  83 | 2021-07-26 00:03:04 | 2021-09-19 23:48:09 | etermin    | Stadt Billerbeck Verwaltung                            |
| [blankenburg](https://www.etermin.net/blankenburg)                                                                  |               2 |            5376 |           787 |                637 |                  32 | 2021-07-26 00:03:04 | 2021-09-19 23:48:10 | etermin    | Stadt Blankenburg (Harz)                               |
| [bonn](https://onlinetermine.bonn.de/index.php?company=stadtbonn)                                                   |               3 |            6713 |          7623 |               6022 |                2513 | 2021-07-12 00:03:33 | 2021-09-19 23:48:43 | netappoint | Stadt Bonn                                             |
| [bonnbau](https://onlinetermine.bonn.de/index.php?company=stadtbonn-bau)                                            |               1 |            6713 |           455 |                 42 |                   2 | 2021-07-12 00:03:38 | 2021-09-19 23:48:06 | netappoint | Stadt Bonn Bauamt                                      |
| [bonnjob](https://www.etermin.net/jcbn)                                                                             |               4 |            5376 |          1287 |                 56 |                 343 | 2021-07-26 00:03:05 | 2021-09-19 23:48:11 | etermin    | Jobcenter Bonn                                         |
| [braunschweigtest](https://www.etermin.net/coronatestbs)                                                            |               1 |             637 |            59 |                 20 |                   1 | 2021-07-26 00:03:05 | 2021-08-01 15:03:18 | etermin    | Corona Test Braunschweig                               |
| [burgendlandkaa](https://www.etermin.net/GBRBgld)                                                                   |               1 |            5376 |           121 |                  5 |                   0 | 2021-07-26 00:03:06 | 2021-09-19 23:48:11 | etermin    | Kammer für Arbeiter und Angestellte für das Burgenland |
| [butzbach](https://www.etermin.net/stadtbutzbach)                                                                   |               2 |            5376 |           989 |                598 |                  81 | 2021-07-26 00:03:06 | 2021-09-19 23:48:12 | etermin    | Magistrat der Stadt Butzbach                           |
| [cochemzell](https://termine-reservieren.de/termine/cochem-zell)                                                    |               6 |            5367 |          3228 |                907 |                 362 | 2021-07-26 00:03:27 | 2021-09-19 23:48:28 | tevis      | Landkreis Cochem-Zell                                  |
| [coesfeld](https://www.etermin.net/coe)                                                                             |               2 |            5376 |           679 |                 98 |                  16 | 2021-07-26 00:03:07 | 2021-09-19 23:48:13 | etermin    | Stadt Coesfeld                                         |
| [daunvg](https://www.etermin.net/vgdaun)                                                                            |               1 |            4673 |           288 |                176 |                  14 | 2021-07-26 00:03:07 | 2021-09-19 23:48:14 | etermin    | Verbandsgemeindeverwaltung Daun                        |
| [dormagen](https://www.etermin.net/stadtdormagen)                                                                   |               2 |            1225 |           294 |                140 |                   4 | 2021-07-26 08:18:09 | 2021-09-14 13:48:13 | etermin    | Stadt Dormagen                                         |
| [dresden](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-fs)                                  |               3 |            6711 |          1732 |               1020 |                 472 | 2021-07-12 00:03:49 | 2021-09-19 23:48:15 | netappoint | Stadt Dresden                                          |
| [dresdenkfz](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-kfz)                              |               4 |            6712 |          5837 |               3665 |                1204 | 2021-07-12 00:04:05 | 2021-09-19 23:48:17 | netappoint | Stadt Dresden Kfz-Zulassungsbehörde                    |
| [duelmen](https://www.etermin.net/duelmen)                                                                          |               9 |            5374 |          4205 |               2630 |                 520 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 | etermin    | Stadt Dülmen                                           |
| [egelsbach](https://tevis.ekom21.de/egb)                                                                            |               3 |            3503 |           575 |                 80 |                  37 | 2021-07-12 00:04:06 | 2021-08-17 14:33:04 | tevis      | Stadt Egelsbach                                        |
| [eislingen](https://termine-reservieren.de/termine/eislingen)                                                       |              16 |            5355 |          4474 |                677 |                 964 | 2021-07-26 00:03:50 | 2021-09-19 23:48:52 | tevis      | Stadt Eislingen                                        |
| [elitheratest](https://www.etermin.net/testzentrum1)                                                                |               1 |             458 |            47 |                 10 |                   9 | 2021-07-26 00:03:22 | 2021-07-31 10:03:50 | etermin    | Corona TESTZENTRUM im Elithera                         |
| [frankenthal](https://termine-reservieren.de/termine/frankenthal)                                                   |               4 |            5361 |          2013 |               1191 |                 564 | 2021-07-26 00:03:57 | 2021-09-19 23:49:00 | tevis      | Stadt Frankenthal                                      |
| [frankfurt](https://tevis.ekom21.de/fra)                                                                            |              15 |            3507 |          9012 |               3608 |                2897 | 2021-07-12 00:04:11 | 2021-08-17 14:33:14 | tevis      | Stadt Frankfurt                                        |
| [friedrichsdorf](https://tevis.ekom21.de/frf)                                                                       |              11 |            3507 |          2509 |                462 |                 129 | 2021-07-12 00:04:13 | 2021-08-17 14:33:19 | tevis      | Stadt Friedrichsdorf                                   |
| [fuerthtest](https://www.etermin.net/Testzentrum_agnf)                                                              |               1 |            5376 |          1922 |                456 |                 421 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 | etermin    | SARS-CoV-2 Testzentrum der Stadt Fürth                 |
| [geldernsw](https://www.etermin.net/Zaehlerwechseltermine)                                                          |               2 |            5375 |          1339 |               1168 |                   0 | 2021-07-26 00:03:23 | 2021-09-19 23:48:31 | etermin    | Stadtwerke Geldern Netz                                |
| [goslartest](https://www.etermin.net/testzentrumgoslar)                                                             |               1 |            5375 |          2026 |               1599 |                 250 | 2021-07-26 00:03:24 | 2021-09-19 23:48:32 | etermin    | Testzentrum Goslar                                     |
| [graz](https://www.etermin.net/stadtgraz)                                                                           |              39 |            5366 |         29446 |              13455 |                2587 | 2021-07-26 00:03:48 | 2021-09-19 23:49:25 | etermin    | Stadt Graz                                             |
| [grazamt](https://www.etermin.net/buergerinnenamt)                                                                  |               9 |            5373 |          4866 |               2258 |                 811 | 2021-07-26 00:03:53 | 2021-09-19 23:49:26 | etermin    | BürgerInnenamt Stadt Graz                              |
| [grazuni](https://www.etermin.net/unitestet)                                                                        |               1 |            3735 |           439 |                  1 |                   0 | 2021-08-12 02:19:47 | 2021-09-19 23:49:28 | etermin    | Universität Graz                                       |
| [gronau](https://termine-reservieren.de/termine/gronau)                                                             |               7 |            5361 |          2241 |               1040 |                 389 | 2021-07-26 00:04:01 | 2021-09-19 23:49:15 | tevis      | Stadt Gronau                                           |
| [grossumstadt](https://tevis.ekom21.de/gad)                                                                         |               3 |            3508 |          1471 |                550 |                 198 | 2021-07-12 00:04:14 | 2021-08-17 14:33:21 | tevis      | Stadt Groß-Umstadt                                     |
| [halbersadt](https://www.etermin.net/halberstadt)                                                                   |               2 |            5375 |           253 |                100 |                   5 | 2021-07-26 00:03:54 | 2021-09-19 23:49:29 | etermin    | Stadt Halberstadt                                      |
| [halle](https://ncu.halle.de/index.php?company=stadthalle)                                                          |              22 |            5376 |          8334 |               5258 |                2079 | 2021-07-26 00:03:31 | 2021-09-19 23:48:31 | netappoint | Stadt Halle                                            |
| [hammersbachtest](https://www.etermin.net/Schnelltestzentrum)                                                       |               3 |            5376 |          6196 |               3205 |                 268 | 2021-07-26 00:03:55 | 2021-09-19 23:49:31 | etermin    | Schnelltestzentrum Hammersbach                         |
| [heidelberg](https://tevis-online.heidelberg.de)                                                                    |               8 |            6715 |          5879 |               2413 |                1364 | 2021-07-12 00:04:15 | 2021-09-19 23:48:04 | tevis      | Stadt Heidelberg                                       |
| [hersfeldtest](https://www.etermin.net/testcenter-hef-rof)                                                          |               1 |            5376 |          1100 |                480 |                 326 | 2021-07-26 00:03:56 | 2021-09-19 23:49:32 | etermin    | Corona-Testcenter Hersfeld-Rotenburg                   |
| [hof](https://termine-reservieren.de/termine/hof)                                                                   |               3 |            5359 |          2169 |               1407 |                 347 | 2021-07-26 00:04:07 | 2021-09-19 23:49:22 | tevis      | Stadt Hof                                              |
| [hornberg](https://tevis.ekom21.de/hbe)                                                                             |               1 |            3508 |           543 |                193 |                  95 | 2021-07-12 00:04:16 | 2021-08-17 14:33:21 | tevis      | Stadt Hornberg                                         |
| [hsktest](https://www.etermin.net/hsk-schnelltest)                                                                  |               1 |            5376 |          1168 |                168 |                  61 | 2021-07-26 00:03:57 | 2021-09-19 23:49:34 | etermin    | Hochsauerlandkreis                                     |
| [huenstetten](https://tevis.ekom21.de/hsz)                                                                          |               4 |            3508 |           675 |                233 |                  61 | 2021-07-12 00:04:17 | 2021-08-17 14:33:24 | tevis      | Stadt Hünstetten                                       |
| [huettenberg](https://tevis.ekom21.de/htb)                                                                          |               9 |            3508 |           851 |                112 |                  35 | 2021-07-12 00:04:21 | 2021-08-17 14:33:30 | tevis      | Stadt Hüttenberg                                       |
| [ilmkreis](https://tvweb.ilm-kreis.de/ilmkreis)                                                                     |               1 |            6464 |             0 |                  0 |                   0 | 2021-07-12 00:04:22 | 2021-09-19 23:48:02 | tevis      | Ilm-Kreis                                              |
| [impfthueringen](https://www.impfen-thueringen.de/terminvergabe)                                                    |              75 |            6713 |        235241 |             133584 |              152720 | 2021-07-12 00:00:00 | 2021-09-19 23:45:00 | custom     | Impftermin Thüringen                                   |
| [ingelheim](https://termine-reservieren.de/termine/ingelheim)                                                       |               1 |            5369 |          1156 |                531 |                 362 | 2021-07-26 00:04:09 | 2021-09-19 23:49:24 | tevis      | Stadt Ingelheim                                        |
| [innsbruckpsych](https://www.etermin.net/PSB-Innsbruck)                                                             |               1 |             984 |            15 |                  2 |                   1 | 2021-07-26 00:03:57 | 2021-09-04 09:51:16 | etermin    | Psychologische Studierendenberatung Innsbruck          |
| [itzehoe](https://www.etermin.net/Stadt_Itzehoe)                                                                    |               3 |            2550 |           408 |                221 |                  21 | 2021-07-26 15:19:04 | 2021-09-19 20:04:34 | etermin    | Stadt Itzehoe Einwohnermeldeamt                        |
| [jena](https://tevis-bs.jena.de)                                                                                    |               6 |            6712 |          8725 |               5647 |                2767 | 2021-07-12 00:04:23 | 2021-09-19 23:48:05 | tevis      | Stadt Jena                                             |
| [kaiserslauternausl](https://www3.kaiserslautern.de/netappoint/index.php?company=kaiserslautern-ausl)               |               2 |            6715 |             0 |                  0 |                   0 | 2021-07-12 00:04:24 | 2021-09-19 23:48:02 | netappoint | Stadt Kaiserslautern Ausländerbehörde                  |
| [kassel](https://tevis.ekom21.de/kas)                                                                               |              14 |            3508 |          7544 |               4065 |                1804 | 2021-07-12 00:04:29 | 2021-08-17 14:33:36 | tevis      | Stadt Kassel                                           |
| [kelsterbach](https://tevis.ekom21.de/keb)                                                                          |               1 |            3508 |           575 |                114 |                  61 | 2021-07-12 00:04:30 | 2021-08-17 14:33:37 | tevis      | Stadt Kelsterbach                                      |
| [kreisbergstrasse](https://terminreservierungverkehr.kreis-bergstrasse.de/netappoint/index.php?company=bergstrasse) |               2 |            6520 |          3295 |               1958 |                 894 | 2021-07-12 00:04:53 | 2021-09-19 23:48:19 | netappoint | Kreis Bergstraße                                       |
| [kreisgermersheimkfz](https://kfz.kreis-germersheim.de/netappoint/index.php?company=kreis-germersheim)              |               1 |            6711 |           573 |                289 |                  88 | 2021-07-12 00:04:55 | 2021-09-19 23:48:03 | netappoint | Kreis Germersheim Kfz-Zulassungsbehörde                |
| [kreisgrossgerau](https://tevis.ekom21.de/grg)                                                                      |              12 |            3321 |          4437 |               1138 |                 917 | 2021-07-12 00:04:59 | 2021-08-17 13:48:44 | tevis      | Kreis Groß-Gerau                                       |
| [kreissteinfurt](https://www.etermin.net/kreis-steinfurt)                                                           |               1 |            1577 |           260 |                181 |                  15 | 2021-07-26 00:03:58 | 2021-08-11 10:05:11 | etermin    | Kreis Steinfurt                                        |
| [kreiswesel](https://tevis.krzn.de/tevisweb080)                                                                     |               4 |            6706 |         10411 |               6731 |                4886 | 2021-07-12 00:05:02 | 2021-09-19 23:48:04 | tevis      | Kreis Wesel                                            |
| [kvmayenkoblenz](https://termine-reservieren.de/termine/kvmayen-koblenz)                                            |               5 |            5362 |          4661 |               2377 |                1285 | 2021-07-26 00:04:22 | 2021-09-19 23:49:34 | tevis      | Landkreis Mayen-Koblenz                                |
| [lehrte](https://www.etermin.net/StadtLehrte)                                                                       |               7 |            5376 |          4031 |               2985 |                 524 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 | etermin    | Stadt Lehrte                                           |
| [leipzig](https://leipzig.de/fachanwendungen/termine/index.html)                                                    |              22 |            5374 |         12375 |               8850 |                1251 | 2021-07-26 00:03:13 | 2021-09-19 23:48:15 | custom     | Stadt Leipzig                                          |
| [leipzigstandesamt](https://adressen.leipzig.de/netappoint/index.php?company=leipzig-standesamt)                    |               3 |            6716 |           866 |                483 |                 175 | 2021-07-12 00:05:04 | 2021-09-19 23:48:04 | netappoint | Stadt Leipzig Standesamt                               |
| [leun](https://tevis.ekom21.de/lnx)                                                                                 |               6 |            1590 |           592 |                 56 |                  11 | 2021-07-12 00:05:05 | 2021-08-17 00:22:10 | tevis      | Stadt Leun                                             |
| [linsengericht](https://tevis.ekom21.de/lsg)                                                                        |               1 |            1461 |           220 |                 34 |                  18 | 2021-07-12 00:05:05 | 2021-08-17 00:22:11 | tevis      | Stadt Linsengericht                                    |
| [loehne](https://termine-reservieren.de/termine/loehne)                                                             |              22 |            5353 |          6724 |                810 |                 152 | 2021-07-26 00:04:53 | 2021-09-19 23:50:06 | tevis      | Stadt Löhne                                            |
| [lramiesbach](https://termine-reservieren.de/termine/lra-miesbach)                                                  |               3 |            5362 |          2537 |               1478 |                 898 | 2021-07-26 00:04:57 | 2021-09-19 23:50:12 | tevis      | Landratsamt Miesbach                                   |
| [lramuenchenefa](https://termine-reservieren.de/termine/lramuenchen/efa)                                            |               3 |            5360 |          1132 |                387 |                 145 | 2021-07-26 00:05:01 | 2021-09-19 23:50:16 | tevis      | Landratsamt München                                    |
| [magdeburg](https://service.magdeburg.de/netappoint/index.php?company=magdeburg)                                    |              27 |            6471 |          7662 |                921 |                 263 | 2021-07-12 00:05:32 | 2021-09-19 23:48:13 | netappoint | Stadt Magdeburg                                        |
| [mainz](https://otv.mainz.de)                                                                                       |              16 |            5349 |         11139 |               7584 |                2290 | 2021-07-26 00:03:22 | 2021-09-19 23:48:22 | tevis      | Stadt Mainz                                            |
| [minden](https://termine-reservieren.de/termine/minden)                                                             |               3 |            5364 |          4451 |               2943 |                1170 | 2021-07-26 00:05:06 | 2021-09-19 23:50:21 | tevis      | Stadt Minden                                           |
| [mittenwalde](https://www.etermin.net/StadtMittenwalde)                                                             |               3 |            5376 |           640 |                 61 |                   4 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 | etermin    | Stadt Mittenwalde                                      |
| [moerlenbach](https://tevis.ekom21.de/mah)                                                                          |               1 |            1375 |           257 |                 20 |                   9 | 2021-07-12 00:05:32 | 2021-08-17 00:22:12 | tevis      | Stadt Mörlenbach                                       |
| [neuisenburg](https://tevis.ekom21.de/nis)                                                                          |               1 |            1334 |           238 |                 24 |                  22 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 | tevis      | Stadt Neu-Isenburg                                     |
| [niedenstein](https://tevis.ekom21.de/nsn)                                                                          |               1 |            1294 |           204 |                 17 |                   4 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 | tevis      | Stadt Niedenstein                                      |
| [nordhausen](https://tevis.svndh.de)                                                                                |               2 |            6715 |          1970 |               1130 |                 662 | 2021-07-12 00:05:35 | 2021-09-19 23:48:04 | tevis      | Stadt Nordhausen                                       |
| [oberasbach](https://www.etermin.net/stadtoberasbach)                                                               |               1 |             633 |            38 |                 10 |                   2 | 2021-07-26 11:04:16 | 2021-09-19 17:04:43 | etermin    | Stadt Oberasbach                                       |
| [oberramstadt](https://tevis.ekom21.de/oby)                                                                         |               6 |            1196 |          1191 |                140 |                 117 | 2021-07-12 00:05:38 | 2021-08-17 00:22:17 | tevis      | Stadt Ober-Ramstadt                                    |
| [oesterreichgk](https://www.etermin.net/OEGK)                                                                       |               3 |            1725 |             0 |                  0 |                   0 | 2021-09-02 00:06:35 | 2021-09-19 23:50:18 | etermin    | Österreichische Gesundheitskasse                       |
| [offenbach](https://tevis.ekom21.de/off)                                                                            |               9 |            1185 |          1522 |                 23 |                   3 | 2021-07-12 00:05:41 | 2021-08-17 00:22:22 | tevis      | Stadt Offenbach                                        |
| [olfen](https://www.etermin.net/stadtolfen)                                                                         |               1 |            5375 |           930 |                441 |                  49 | 2021-07-26 00:04:18 | 2021-09-19 23:50:18 | etermin    | Stadt Olfen                                            |
| [paderborn](https://termine-reservieren.de/termine/paderborn)                                                       |              15 |            5357 |         11977 |               5303 |                3648 | 2021-07-26 00:05:36 | 2021-09-19 23:50:53 | tevis      | Stadt Paderborn                                        |
| [pfungstadt](https://tevis.ekom21.de/pft)                                                                           |               2 |            1170 |           520 |                 89 |                  55 | 2021-07-12 00:05:43 | 2021-08-13 23:34:33 | tevis      | Stadt Pfungstadt                                       |
| [salzgitter](https://termine-reservieren.de/termine/salzgitter)                                                     |              26 |            5355 |          6879 |               2726 |                1098 | 2021-07-26 00:06:21 | 2021-09-19 23:51:39 | tevis      | Stadt Salzgitter                                       |
| [schoenebeckelbe](https://termine-reservieren.de/termine/schoenebeck-elbe)                                          |               1 |            5365 |           352 |                178 |                  70 | 2021-07-26 00:06:23 | 2021-09-19 23:51:41 | tevis      | Stadt Schönebeck (Elbe)                                |
| [selm](https://www.etermin.net/stadtselm)                                                                           |               2 |            1687 |            84 |                 41 |                   2 | 2021-07-26 09:49:51 | 2021-09-19 23:50:19 | etermin    | Stadt Selm                                             |
| [speyer](https://termine-reservieren.de/termine/speyer)                                                             |               6 |            5364 |          1329 |                723 |                 185 | 2021-07-26 00:06:26 | 2021-09-19 23:51:45 | tevis      | Stadt Speyer                                           |
| [stadtbergen](https://www.etermin.net/stadtbergen)                                                                  |               2 |            5292 |           683 |                197 |                 221 | 2021-07-26 00:04:20 | 2021-09-19 23:50:19 | etermin    | Stadt Stadtbergen                                      |
| [stadtsoest](https://termine-reservieren.de/termine/stadtsoest)                                                     |               1 |            5366 |          1813 |               1253 |                 776 | 2021-07-26 00:06:28 | 2021-09-19 23:51:48 | tevis      | Stadt Söst                                             |
| [steinburg](https://termine-reservieren.de/termine/steinburg)                                                       |               2 |            5365 |           182 |                  4 |                   3 | 2021-07-26 00:06:32 | 2021-09-19 23:51:52 | tevis      | Stadt Steinburg                                        |
| [teublitztest](https://www.etermin.net/spitzwegapo)                                                                 |               1 |            5376 |          1098 |                642 |                 257 | 2021-07-26 00:04:21 | 2021-09-19 23:50:20 | etermin    | Corona-Schnellteststelle Teublitz                      |
| [trier](https://termine-reservieren.de/termine/trier)                                                               |               5 |            5357 |          2048 |                877 |                 361 | 2021-07-26 00:06:43 | 2021-09-19 23:52:05 | tevis      | Stadt Trier                                            |
| [unna](https://termine-reservieren.de/termine/unna)                                                                 |               2 |            5363 |          1586 |                937 |                 593 | 2021-07-26 00:06:46 | 2021-09-19 23:52:08 | tevis      | Stadt Unna                                             |
| [viernheim](https://tevis.ekom21.de/vhx)                                                                            |               1 |            1169 |           315 |                 52 |                  31 | 2021-07-12 00:05:43 | 2021-08-13 23:34:34 | tevis      | Stadt Viernheim                                        |
| [weilheimschongau](https://termine-reservieren.de/termine/weilheimschongau)                                         |               2 |            5361 |           738 |                315 |                  98 | 2021-07-26 00:06:51 | 2021-09-19 23:52:11 | tevis      | Landkreis Weilheim-Schongau                            |
| [weimar](https://tevis.weimar.de)                                                                                   |               1 |            6712 |          1994 |                862 |                 717 | 2021-07-12 00:05:44 | 2021-09-19 23:48:03 | tevis      | Stadt Weimar                                           |
| [weiterstadt](https://tevis.ekom21.de/wdt)                                                                          |               2 |            1135 |           581 |                 51 |                  19 | 2021-07-12 00:05:45 | 2021-08-09 15:34:56 | tevis      | Stadt Weiterstadt                                      |
| [wiehl](https://www.etermin.net/stadtwiehl)                                                                         |               1 |             107 |             5 |                  0 |                   0 | 2021-07-27 09:34:23 | 2021-09-07 10:36:52 | etermin    | Stadt Wiehl                                            |
| [wittmund](https://termine-reservieren.de/termine/wittmund/stva)                                                    |               3 |            5356 |          1598 |                644 |                 387 | 2021-07-26 00:06:56 | 2021-09-19 23:52:16 | tevis      | Stadt Wittmund                                         |
| [worms](https://termine-reservieren.de/termine/worms)                                                               |               6 |            5358 |          5063 |               3284 |                1782 | 2021-07-26 00:07:06 | 2021-09-19 23:52:28 | tevis      | Stadt Worms                                            |

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

