## History of free office appointment dates (in Germany)

This is the data export of [office-schedule-scraper](https://github.com/defgsus/office-schedule-scraper/).

The data contains the **free dates** where one can make an appointment at a 
public office at a snapshot interval of 15 minutes, starting at 2021-07-12.


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
        "location_name": "name of office/building",
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

# Statistics

Repository last updated at **2021-09-20**
 
**98** sources,
**575** locations,
**441160** snapshots

- [snapshots-weekly.csv](statistics/snapshots-weekly.csv) contains the number of 
  snapshots per calendar week and `source_id`
- [snapshots-sum.csv](statistics/snapshots-sum.csv) (below table) contains
  the sum of snapshots per `source_id`

| source_id                                                                                                            | name                                                   | scraper    |   num_locations |   num_snapshots |   num_changes | min_date            | max_date            |
|:---------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|:-----------|----------------:|----------------:|--------------:|:--------------------|:--------------------|
| [amberg](https://termine.amberg.de/)                                                                                 | Stadt Amberg                                           | tevis      |               4 |            5374 |          2010 | 2021-07-26 00:03:02 | 2021-09-19 23:48:04 |
| [badkreuznach](https://termine-reservieren.de/termine/svkh/)                                                         | Stadt Bad-Kreuznach                                    | tevis      |               4 |            5356 |          3156 | 2021-07-26 00:03:10 | 2021-09-19 23:48:13 |
| [bbmess](https://www.etermin.net/lme-be-bb/)                                                                         | Landesamt für Mess- und Eichwesen Berlin-Brandenburg   | etermin    |               2 |            3728 |           466 | 2021-07-26 00:03:02 | 2021-09-17 08:33:04 |
| [bernkastelwittlich](https://termine-reservieren.de/termine/bernkastel-wittlich/)                                    | Landkreis Bernkastel-Wittlich                          | tevis      |               3 |            5365 |          3537 | 2021-07-26 00:03:17 | 2021-09-19 23:48:17 |
| [billerbeck](https://www.etermin.net/termininbillerbeck/)                                                            | Stadt Billerbeck Verwaltung                            | etermin    |               3 |            5376 |          1053 | 2021-07-26 00:03:04 | 2021-09-19 23:48:09 |
| [blankenburg](https://www.etermin.net/blankenburg/)                                                                  | Stadt Blankenburg (Harz)                               | etermin    |               2 |            5376 |           787 | 2021-07-26 00:03:04 | 2021-09-19 23:48:10 |
| [bonn](https://onlinetermine.bonn.de/index.php?company=stadtbonn/)                                                   | Stadt Bonn                                             | netappoint |               3 |            6713 |          7623 | 2021-07-12 00:03:33 | 2021-09-19 23:48:43 |
| [bonnbau](https://onlinetermine.bonn.de/index.php?company=stadtbonn-bau/)                                            | Stadt Bonn Bauamt                                      | netappoint |               1 |            6713 |           455 | 2021-07-12 00:03:38 | 2021-09-19 23:48:06 |
| [bonnjob](https://www.etermin.net/jcbn/)                                                                             | Jobcenter Bonn                                         | etermin    |               4 |            5376 |          1287 | 2021-07-26 00:03:05 | 2021-09-19 23:48:11 |
| [braunschweigtest](https://www.etermin.net/coronatestbs/)                                                            | Corona Test Braunschweig                               | etermin    |               1 |             637 |            59 | 2021-07-26 00:03:05 | 2021-08-01 15:03:18 |
| [burgendlandkaa](https://www.etermin.net/GBRBgld/)                                                                   | Kammer für Arbeiter und Angestellte für das Burgenland | etermin    |               1 |            5376 |           121 | 2021-07-26 00:03:06 | 2021-09-19 23:48:11 |
| [butzbach](https://www.etermin.net/stadtbutzbach/)                                                                   | Magistrat der Stadt Butzbach                           | etermin    |               2 |            5376 |           989 | 2021-07-26 00:03:06 | 2021-09-19 23:48:12 |
| [cochemzell](https://termine-reservieren.de/termine/cochem-zell/)                                                    | Landkreis Cochem-Zell                                  | tevis      |               6 |            5367 |          3228 | 2021-07-26 00:03:27 | 2021-09-19 23:48:28 |
| [coesfeld](https://www.etermin.net/coe/)                                                                             | Stadt Coesfeld                                         | etermin    |               2 |            5376 |           679 | 2021-07-26 00:03:07 | 2021-09-19 23:48:13 |
| [daunvg](https://www.etermin.net/vgdaun/)                                                                            | Verbandsgemeindeverwaltung Daun                        | etermin    |               1 |            4673 |           288 | 2021-07-26 00:03:07 | 2021-09-19 23:48:14 |
| [dormagen](https://www.etermin.net/stadtdormagen/)                                                                   | Stadt Dormagen                                         | etermin    |               2 |            1225 |           294 | 2021-07-26 08:18:09 | 2021-09-14 13:48:13 |
| [dresden](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-fs/)                                  | Stadt Dresden                                          | netappoint |               3 |            6711 |          1732 | 2021-07-12 00:03:49 | 2021-09-19 23:48:15 |
| [dresdenkfz](https://termine.dresden.de/netappoint/index.php?company=stadtdresden-kfz/)                              | Stadt Dresden Kfz-Zulassungsbehörde                    | netappoint |               4 |            6712 |          5837 | 2021-07-12 00:04:05 | 2021-09-19 23:48:17 |
| [duelmen](https://www.etermin.net/duelmen/)                                                                          | Stadt Dülmen                                           | etermin    |               9 |            5374 |          4205 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 |
| [egelsbach](https://tevis.ekom21.de/egb/)                                                                            | Stadt Egelsbach                                        | tevis      |               3 |            3503 |           575 | 2021-07-12 00:04:06 | 2021-08-17 14:33:04 |
| [eislingen](https://termine-reservieren.de/termine/eislingen/)                                                       | Stadt Eislingen                                        | tevis      |              16 |            5355 |          4474 | 2021-07-26 00:03:50 | 2021-09-19 23:48:52 |
| [elitheratest](https://www.etermin.net/testzentrum1/)                                                                | Corona TESTZENTRUM im Elithera                         | etermin    |               1 |             458 |            47 | 2021-07-26 00:03:22 | 2021-07-31 10:03:50 |
| [frankenthal](https://termine-reservieren.de/termine/frankenthal/)                                                   | Stadt Frankenthal                                      | tevis      |               4 |            5361 |          2013 | 2021-07-26 00:03:57 | 2021-09-19 23:49:00 |
| [frankfurt](https://tevis.ekom21.de/fra/)                                                                            | Stadt Frankfurt                                        | tevis      |              15 |            3507 |          9012 | 2021-07-12 00:04:11 | 2021-08-17 14:33:14 |
| [friedrichsdorf](https://tevis.ekom21.de/frf/)                                                                       | Stadt Friedrichsdorf                                   | tevis      |              11 |            3507 |          2509 | 2021-07-12 00:04:13 | 2021-08-17 14:33:19 |
| [fuerthtest](https://www.etermin.net/Testzentrum_agnf/)                                                              | SARS-CoV-2 Testzentrum der Stadt Fürth                 | etermin    |               1 |            5376 |          1922 | 2021-07-26 00:03:22 | 2021-09-19 23:48:30 |
| [geldernsw](https://www.etermin.net/Zaehlerwechseltermine/)                                                          | Stadtwerke Geldern Netz                                | etermin    |               2 |            5375 |          1339 | 2021-07-26 00:03:23 | 2021-09-19 23:48:31 |
| [goslartest](https://www.etermin.net/testzentrumgoslar/)                                                             | Testzentrum Goslar                                     | etermin    |               1 |            5375 |          2026 | 2021-07-26 00:03:24 | 2021-09-19 23:48:32 |
| [graz](https://www.etermin.net/stadtgraz/)                                                                           | Stadt Graz                                             | etermin    |              39 |            5366 |         29446 | 2021-07-26 00:03:48 | 2021-09-19 23:49:25 |
| [grazamt](https://www.etermin.net/buergerinnenamt/)                                                                  | BürgerInnenamt Stadt Graz                              | etermin    |               9 |            5373 |          4866 | 2021-07-26 00:03:53 | 2021-09-19 23:49:26 |
| [grazuni](https://www.etermin.net/unitestet/)                                                                        | Universität Graz                                       | etermin    |               1 |            3735 |           439 | 2021-08-12 02:19:47 | 2021-09-19 23:49:28 |
| [gronau](https://termine-reservieren.de/termine/gronau/)                                                             | Stadt Gronau                                           | tevis      |               7 |            5361 |          2241 | 2021-07-26 00:04:01 | 2021-09-19 23:49:15 |
| [grossumstadt](https://tevis.ekom21.de/gad/)                                                                         | Stadt Groß-Umstadt                                     | tevis      |               3 |            3508 |          1471 | 2021-07-12 00:04:14 | 2021-08-17 14:33:21 |
| [halbersadt](https://www.etermin.net/halberstadt/)                                                                   | Stadt Halberstadt                                      | etermin    |               2 |            5375 |           253 | 2021-07-26 00:03:54 | 2021-09-19 23:49:29 |
| [halle](https://ncu.halle.de/index.php?company=stadthalle/)                                                          | Stadt Halle                                            | netappoint |              22 |            5376 |          8334 | 2021-07-26 00:03:31 | 2021-09-19 23:48:31 |
| [hammersbachtest](https://www.etermin.net/Schnelltestzentrum/)                                                       | Schnelltestzentrum Hammersbach                         | etermin    |               3 |            5376 |          6196 | 2021-07-26 00:03:55 | 2021-09-19 23:49:31 |
| [heidelberg](https://tevis-online.heidelberg.de/)                                                                    | Stadt Heidelberg                                       | tevis      |               8 |            6715 |          5879 | 2021-07-12 00:04:15 | 2021-09-19 23:48:04 |
| [hersfeldtest](https://www.etermin.net/testcenter-hef-rof/)                                                          | Corona-Testcenter Hersfeld-Rotenburg                   | etermin    |               1 |            5376 |          1100 | 2021-07-26 00:03:56 | 2021-09-19 23:49:32 |
| [hof](https://termine-reservieren.de/termine/hof/)                                                                   | Stadt Hof                                              | tevis      |               3 |            5359 |          2169 | 2021-07-26 00:04:07 | 2021-09-19 23:49:22 |
| [hornberg](https://tevis.ekom21.de/hbe/)                                                                             | Stadt Hornberg                                         | tevis      |               1 |            3508 |           543 | 2021-07-12 00:04:16 | 2021-08-17 14:33:21 |
| [hsktest](https://www.etermin.net/hsk-schnelltest/)                                                                  | Hochsauerlandkreis                                     | etermin    |               1 |            5376 |          1168 | 2021-07-26 00:03:57 | 2021-09-19 23:49:34 |
| [huenstetten](https://tevis.ekom21.de/hsz/)                                                                          | Stadt Hünstetten                                       | tevis      |               4 |            3508 |           675 | 2021-07-12 00:04:17 | 2021-08-17 14:33:24 |
| [huettenberg](https://tevis.ekom21.de/htb/)                                                                          | Stadt Hüttenberg                                       | tevis      |               9 |            3508 |           851 | 2021-07-12 00:04:21 | 2021-08-17 14:33:30 |
| [ilmkreis](https://tvweb.ilm-kreis.de/ilmkreis/)                                                                     | Ilm-Kreis                                              | tevis      |               1 |            6464 |             0 | 2021-07-12 00:04:22 | 2021-09-19 23:48:02 |
| [impfthueringen](https://www.impfen-thueringen.de/terminvergabe/)                                                    | Impftermin Thüringen                                   | custom     |              75 |            6713 |        235241 | 2021-07-12 00:00:00 | 2021-09-19 23:45:00 |
| [ingelheim](https://termine-reservieren.de/termine/ingelheim/)                                                       | Stadt Ingelheim                                        | tevis      |               1 |            5369 |          1156 | 2021-07-26 00:04:09 | 2021-09-19 23:49:24 |
| [innsbruckpsych](https://www.etermin.net/PSB-Innsbruck/)                                                             | Psychologische Studierendenberatung Innsbruck          | etermin    |               1 |             984 |            15 | 2021-07-26 00:03:57 | 2021-09-04 09:51:16 |
| [itzehoe](https://www.etermin.net/Stadt_Itzehoe/)                                                                    | Stadt Itzehoe Einwohnermeldeamt                        | etermin    |               3 |            2550 |           408 | 2021-07-26 15:19:04 | 2021-09-19 20:04:34 |
| [jena](https://tevis-bs.jena.de/)                                                                                    | Stadt Jena                                             | tevis      |               6 |            6712 |          8725 | 2021-07-12 00:04:23 | 2021-09-19 23:48:05 |
| [kaiserslauternausl](https://www3.kaiserslautern.de/netappoint/index.php?company=kaiserslautern-ausl/)               | Stadt Kaiserslautern Ausländerbehörde                  | netappoint |               2 |            6715 |             0 | 2021-07-12 00:04:24 | 2021-09-19 23:48:02 |
| [kassel](https://tevis.ekom21.de/kas/)                                                                               | Stadt Kassel                                           | tevis      |              14 |            3508 |          7544 | 2021-07-12 00:04:29 | 2021-08-17 14:33:36 |
| [kelsterbach](https://tevis.ekom21.de/keb/)                                                                          | Stadt Kelsterbach                                      | tevis      |               1 |            3508 |           575 | 2021-07-12 00:04:30 | 2021-08-17 14:33:37 |
| [kreisbergstrasse](https://terminreservierungverkehr.kreis-bergstrasse.de/netappoint/index.php?company=bergstrasse/) | Kreis Bergstraße                                       | netappoint |               2 |            6520 |          3295 | 2021-07-12 00:04:53 | 2021-09-19 23:48:19 |
| [kreisgermersheimkfz](https://kfz.kreis-germersheim.de/netappoint/index.php?company=kreis-germersheim/)              | Kreis Germersheim Kfz-Zulassungsbehörde                | netappoint |               1 |            6711 |           573 | 2021-07-12 00:04:55 | 2021-09-19 23:48:03 |
| [kreisgrossgerau](https://tevis.ekom21.de/grg/)                                                                      | Kreis Groß-Gerau                                       | tevis      |              12 |            3321 |          4437 | 2021-07-12 00:04:59 | 2021-08-17 13:48:44 |
| [kreissteinfurt](https://www.etermin.net/kreis-steinfurt/)                                                           | Kreis Steinfurt                                        | etermin    |               1 |            1577 |           260 | 2021-07-26 00:03:58 | 2021-08-11 10:05:11 |
| [kreiswesel](https://tevis.krzn.de/tevisweb080/)                                                                     | Kreis Wesel                                            | tevis      |               4 |            6706 |         10411 | 2021-07-12 00:05:02 | 2021-09-19 23:48:04 |
| [kvmayenkoblenz](https://termine-reservieren.de/termine/kvmayen-koblenz/)                                            | Landkreis Mayen-Koblenz                                | tevis      |               5 |            5362 |          4661 | 2021-07-26 00:04:22 | 2021-09-19 23:49:34 |
| [lehrte](https://www.etermin.net/StadtLehrte/)                                                                       | Stadt Lehrte                                           | etermin    |               7 |            5376 |          4031 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 |
| [leipzig](https://leipzig.de/fachanwendungen/termine/index.html/)                                                    | Stadt Leipzig                                          | custom     |              22 |            5374 |         12375 | 2021-07-26 00:03:13 | 2021-09-19 23:48:15 |
| [leipzigstandesamt](https://adressen.leipzig.de/netappoint/index.php?company=leipzig-standesamt/)                    | Stadt Leipzig Standesamt                               | netappoint |               3 |            6716 |           866 | 2021-07-12 00:05:04 | 2021-09-19 23:48:04 |
| [leun](https://tevis.ekom21.de/lnx/)                                                                                 | Stadt Leun                                             | tevis      |               6 |            1590 |           592 | 2021-07-12 00:05:05 | 2021-08-17 00:22:10 |
| [linsengericht](https://tevis.ekom21.de/lsg/)                                                                        | Stadt Linsengericht                                    | tevis      |               1 |            1461 |           220 | 2021-07-12 00:05:05 | 2021-08-17 00:22:11 |
| [loehne](https://termine-reservieren.de/termine/loehne/)                                                             | Stadt Löhne                                            | tevis      |              22 |            5353 |          6724 | 2021-07-26 00:04:53 | 2021-09-19 23:50:06 |
| [lramiesbach](https://termine-reservieren.de/termine/lra-miesbach/)                                                  | Landratsamt Miesbach                                   | tevis      |               3 |            5362 |          2537 | 2021-07-26 00:04:57 | 2021-09-19 23:50:12 |
| [lramuenchenefa](https://termine-reservieren.de/termine/lramuenchen/efa/)                                            | Landratsamt München                                    | tevis      |               3 |            5360 |          1132 | 2021-07-26 00:05:01 | 2021-09-19 23:50:16 |
| [magdeburg](https://service.magdeburg.de/netappoint/index.php?company=magdeburg/)                                    | Stadt Magdeburg                                        | netappoint |              27 |            6471 |          7662 | 2021-07-12 00:05:32 | 2021-09-19 23:48:13 |
| [mainz](https://otv.mainz.de/)                                                                                       | Stadt Mainz                                            | tevis      |              16 |            5349 |         11139 | 2021-07-26 00:03:22 | 2021-09-19 23:48:22 |
| [minden](https://termine-reservieren.de/termine/minden/)                                                             | Stadt Minden                                           | tevis      |               3 |            5364 |          4451 | 2021-07-26 00:05:06 | 2021-09-19 23:50:21 |
| [mittenwalde](https://www.etermin.net/StadtMittenwalde/)                                                             | Stadt Mittenwalde                                      | etermin    |               3 |            5376 |           640 | 2021-07-26 00:04:06 | 2021-09-19 23:49:41 |
| [moerlenbach](https://tevis.ekom21.de/mah/)                                                                          | Stadt Mörlenbach                                       | tevis      |               1 |            1375 |           257 | 2021-07-12 00:05:32 | 2021-08-17 00:22:12 |
| [neuisenburg](https://tevis.ekom21.de/nis/)                                                                          | Stadt Neu-Isenburg                                     | tevis      |               1 |            1334 |           238 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 |
| [niedenstein](https://tevis.ekom21.de/nsn/)                                                                          | Stadt Niedenstein                                      | tevis      |               1 |            1294 |           204 | 2021-07-12 00:05:33 | 2021-08-17 00:22:13 |
| [nordhausen](https://tevis.svndh.de/)                                                                                | Stadt Nordhausen                                       | tevis      |               2 |            6715 |          1970 | 2021-07-12 00:05:35 | 2021-09-19 23:48:04 |
| [oberasbach](https://www.etermin.net/stadtoberasbach/)                                                               | Stadt Oberasbach                                       | etermin    |               1 |             633 |            38 | 2021-07-26 11:04:16 | 2021-09-19 17:04:43 |
| [oberramstadt](https://tevis.ekom21.de/oby/)                                                                         | Stadt Ober-Ramstadt                                    | tevis      |               6 |            1196 |          1191 | 2021-07-12 00:05:38 | 2021-08-17 00:22:17 |
| [oesterreichgk](https://www.etermin.net/OEGK/)                                                                       | Österreichische Gesundheitskasse                       | etermin    |               3 |            1725 |             0 | 2021-09-02 00:06:35 | 2021-09-19 23:50:18 |
| [offenbach](https://tevis.ekom21.de/off/)                                                                            | Stadt Offenbach                                        | tevis      |               9 |            1185 |          1522 | 2021-07-12 00:05:41 | 2021-08-17 00:22:22 |
| [olfen](https://www.etermin.net/stadtolfen/)                                                                         | Stadt Olfen                                            | etermin    |               1 |            5375 |           930 | 2021-07-26 00:04:18 | 2021-09-19 23:50:18 |
| [paderborn](https://termine-reservieren.de/termine/paderborn/)                                                       | Stadt Paderborn                                        | tevis      |              15 |            5357 |         11977 | 2021-07-26 00:05:36 | 2021-09-19 23:50:53 |
| [pfungstadt](https://tevis.ekom21.de/pft/)                                                                           | Stadt Pfungstadt                                       | tevis      |               2 |            1170 |           520 | 2021-07-12 00:05:43 | 2021-08-13 23:34:33 |
| [salzgitter](https://termine-reservieren.de/termine/salzgitter/)                                                     | Stadt Salzgitter                                       | tevis      |              26 |            5355 |          6879 | 2021-07-26 00:06:21 | 2021-09-19 23:51:39 |
| [schoenebeckelbe](https://termine-reservieren.de/termine/schoenebeck-elbe/)                                          | Stadt Schönebeck (Elbe)                                | tevis      |               1 |            5365 |           352 | 2021-07-26 00:06:23 | 2021-09-19 23:51:41 |
| [selm](https://www.etermin.net/stadtselm/)                                                                           | Stadt Selm                                             | etermin    |               2 |            1687 |            84 | 2021-07-26 09:49:51 | 2021-09-19 23:50:19 |
| [speyer](https://termine-reservieren.de/termine/speyer/)                                                             | Stadt Speyer                                           | tevis      |               6 |            5364 |          1329 | 2021-07-26 00:06:26 | 2021-09-19 23:51:45 |
| [stadtbergen](https://www.etermin.net/stadtbergen/)                                                                  | Stadt Stadtbergen                                      | etermin    |               2 |            5292 |           683 | 2021-07-26 00:04:20 | 2021-09-19 23:50:19 |
| [stadtsoest](https://termine-reservieren.de/termine/stadtsoest/)                                                     | Stadt Söst                                             | tevis      |               1 |            5366 |          1813 | 2021-07-26 00:06:28 | 2021-09-19 23:51:48 |
| [steinburg](https://termine-reservieren.de/termine/steinburg/)                                                       | Stadt Steinburg                                        | tevis      |               2 |            5365 |           182 | 2021-07-26 00:06:32 | 2021-09-19 23:51:52 |
| [teublitztest](https://www.etermin.net/spitzwegapo/)                                                                 | Corona-Schnellteststelle Teublitz                      | etermin    |               1 |            5376 |          1098 | 2021-07-26 00:04:21 | 2021-09-19 23:50:20 |
| [trier](https://termine-reservieren.de/termine/trier/)                                                               | Stadt Trier                                            | tevis      |               5 |            5357 |          2048 | 2021-07-26 00:06:43 | 2021-09-19 23:52:05 |
| [unna](https://termine-reservieren.de/termine/unna/)                                                                 | Stadt Unna                                             | tevis      |               2 |            5363 |          1586 | 2021-07-26 00:06:46 | 2021-09-19 23:52:08 |
| [viernheim](https://tevis.ekom21.de/vhx/)                                                                            | Stadt Viernheim                                        | tevis      |               1 |            1169 |           315 | 2021-07-12 00:05:43 | 2021-08-13 23:34:34 |
| [weilheimschongau](https://termine-reservieren.de/termine/weilheimschongau/)                                         | Landkreis Weilheim-Schongau                            | tevis      |               2 |            5361 |           738 | 2021-07-26 00:06:51 | 2021-09-19 23:52:11 |
| [weimar](https://tevis.weimar.de/)                                                                                   | Stadt Weimar                                           | tevis      |               1 |            6712 |          1994 | 2021-07-12 00:05:44 | 2021-09-19 23:48:03 |
| [weiterstadt](https://tevis.ekom21.de/wdt/)                                                                          | Stadt Weiterstadt                                      | tevis      |               2 |            1135 |           581 | 2021-07-12 00:05:45 | 2021-08-09 15:34:56 |
| [wiehl](https://www.etermin.net/stadtwiehl/)                                                                         | Stadt Wiehl                                            | etermin    |               1 |             107 |             5 | 2021-07-27 09:34:23 | 2021-09-07 10:36:52 |
| [wittmund](https://termine-reservieren.de/termine/wittmund/stva/)                                                    | Stadt Wittmund                                         | tevis      |               3 |            5356 |          1598 | 2021-07-26 00:06:56 | 2021-09-19 23:52:16 |
| [worms](https://termine-reservieren.de/termine/worms/)                                                               | Stadt Worms                                            | tevis      |               6 |            5358 |          5063 | 2021-07-26 00:07:06 | 2021-09-19 23:52:28 |
