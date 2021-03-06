from pathlib import Path
import os

import numpy as np
import pandas as pd
from shapely import geometry, ops
from shapely.wkt import loads

from src.helper_functions import try_wkt_conversion, convert_coord

# --- import data ---
import_dicts = [
    {
        "tag": "ferry-terminals",
        "path": Path("data/raw/geolocation/ferry-terminals-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ";",
        "headers": [
            "terminal-name",
            "has-line",
            "turu_iskele",
            "globalid",
            "shape-data",
        ],
        "skiprows": 0,
    },
    {
        "tag": "ferry-lines",
        "path": Path("data/raw/geolocation/ferry-lines-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ",",
        "headers": [
            "line-name",
            "isim_kurum",
            "tur_hat",
            "website",
            "globalid",
            "shape-data",
        ],
        "skiprows": 1,
    },
    {
        "tag": "trips-per-ferry-line",
        "path": Path("data/raw/summary-stats/trips-per-ferry-line_2020.csv"),
        "encoding": "utf-8",
        "sep": ";",
        "headers": ["year", "line-name", "n-trips"],
        "skiprows": 1,
    },
    {
        "tag": "transportation-load",
        "path": Path("data/raw/historic-transportation-load/"),
        "encoding": "utf-8",
        "sep": ",",
    },
    {
        "tag": "automated-weather-stations",
        "path": Path("data/raw/geolocation/automated-weather-stations-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ";",
        "headers": ["station-header", "station-name", "shape-data"],
        "skiprows": 1,
    },
    {
        "tag": "icing-sensors",
        "path": Path("data/raw/geolocation/icing-sensors-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ",",
        "headers": ["station-header", "station-name_1", "station_name-2", "shape-data"],
        "skiprows": 1,
    },
    {
        "tag": "weather-observations",
        "path": Path("data/raw/historic-weather-observations/"),
        "encoding": "utf-8",
        "sep": ",",
    },
]
datasets = {}
for import_dict in import_dicts:
    if import_dict["tag"] not in {"transportation-load", "weather-observations"}:
        datasets[import_dict["tag"]] = pd.read_csv(
            import_dict["path"],
            encoding=import_dict["encoding"],
            sep=import_dict["sep"],
            names=import_dict["headers"],
            skiprows=import_dict["skiprows"],
        )
    else:
        # get all subfiles
        dir_list = os.listdir(import_dict["path"])
        # get first element as big dict
        big_df = pd.read_csv(
            os.path.join(import_dict["path"], dir_list[0]),
            encoding=import_dict["encoding"],
            sep=import_dict["sep"],
        )
        for dir in dir_list[1:]:
            temp_df = pd.read_csv(
                os.path.join(import_dict["path"], dir),
                encoding=import_dict["encoding"],
                sep=import_dict["sep"],
            )
            big_df = big_df.append(temp_df, ignore_index=True)
        datasets[import_dict["tag"]] = big_df

# --- clean 'ferry-terminals-geoloc.csv' ---
dataset = datasets["ferry-terminals"]

# filter by 'turu_iskele' (terminal type)
dataset = dataset.loc[dataset["turu_iskele"] == "IDO ??ehir Hatlar??", :]

# drop unnecessary columns
dataset = dataset.drop(["globalid", "turu_iskele"], axis=1)

# fix values in the 'terminal-name' column
# code here is extremely verbose and not using any regex to fix commonly
# occuring patterns on purpose because I am using real-life knowledge to
# correct data quality.
repl_dict = {
    "Anadolu Hisar?? ??H.": "Anadolu Hisar??",
    "Kabata?? ??H.": "Kabata??",
    "Kad??k??y-Be??ikta??-Adalar ??H.": "Kad??k??y - Be??ikta?? - Adalar",
    "Kandilli ??H.": "Kandilli",
    "Kanl??ca ??H.": "Kanl??ca",
    "Karak??y ??H.": "Karak??y",
    "Kas??mpa??a ??H.": "Kas??mpa??a",
    "Kuzguncuk ??H.": "Kuzguncuk",
    "K??????ksu ??H.": "K??????ksu",
    "K??nal??ada ??H.": "K??nal??ada",
    "Ortak??y ??H.": "Ortak??y",
    "Pa??abah??e ??H.": "Pa??abah??e",
    "Rumeli Kava???? ??H.": "Rumeli Kava????",
    "Sar??yer ??H.": "Sar??yer",
    "Sedef Adas?? ??H.": "Sedef Adas??",
    "S??tl??ce ??H.": "S??tl??ce",
    "Yeni Kad??k??y ??H.": "Yeni Kad??k??y",
    "Yenik??y ??H.": "Yenik??y",
    "??engelk??y ??H.": "??engelk??y",
    "??ubuklu ??H.": "??ubuklu",
    "??ubuklu ??H. (Arabal?? Vapur)": "??ubuklu Car Ferry Terminal",
    "??sk??dar ??H.": "??sk??dar",
    "??stinye ??H.": "??stinye",
    "Kad??k??y-Be??ikta?? ??H.": "Kad??k??y - Be??ikta??",
    "Heybeliada ??H.": "Heybeliada",
    "Anadolu Kava???? ??H.": "Anadolu Kava????",
    "Haydarpa??a ??H.": "Haydarpa??a",
    "Arnavutk??y ??H.": "Arnavutk??y",
    "Ayvansaray ??H.": "Ayvansaray",
    "Balat ??H.": "Balat",
    "Bebek ??H.": "Bebek",
    "Beykoz ??H.": "Beykoz",
    "Beylerbeyi ??H.": "Beylerbeyi",
    "Be??ikta??-Kad??k??y ??H.": "Be??ikta?? - Kad??k??y",
    "Be??ikta??-??sk??dar ??H.": "Be??ikta?? - ??sk??dar",
    "Bostanc?? ??H.": "Bostanc??",
    "Burgazada ??H.": "Burgazada",
    "B??y??kada ??H.": "B??y??kada",
    "B??y??kdere ??H.": "B??y??kdere",
    "Emin??n?? Caml?? ??skele ??H.": "Emin??n?? Small Terminal",
    "Emin??n??-Bo??az ??H.": "Emin??n?? - Bosphorus",
    "Emin??n??-Hali?? ??H.": "Emin??n?? Hali??",
    "Emin??n??-Kad??k??y ??H.": "Emin??n?? - Kad??k??y",
    "Emin??n??-??sk??dar ??H.": "Emin??n?? - ??sk??dar",
    "Emirgan ??H.": "Emirgan",
    "Ey??p ??H.": "Ey??p",
    "Fener ??H.": "Fener",
    "Hask??y ??H.": "Hask??y",
    "??stinye ??H. (Arabal?? Vapur)": "??stinye Car Ferry Terminal",
}
dataset = dataset.replace(repl_dict)

# fix values in the 'has-line' column
repl_dict = {
    "Hatt??": "Line",
    "Bo??az": "Bosphorus",
    "Kabata??": "Kabata??",
    "Kad??k??y": "Kad??k??y",
    "Be??ikta??": "Be??ikta??",
    "BE????KTA??": "Be??ikta??",
    "MUHTEL??F": "Muhtelif",
    "Sar??yer": "Sar??yer",
    "Kava????": "Kava????",
    "??stinye": "??stinye",
    "Arabal?? Vapur": "Car Ferry",
    "Bostanc??": "Bostanc??",
    "Adas??": "Adas??",
    "Haydarpa??a": "Haydarpa??a",
    "Bostanc??": "Bostanc??",
    "EM??N??N??": "Emin??n??",
    "??ST??NYE": "??stinye",
    "EM??RGAN": "Emirgan",
    "BEYLERBEY??": "Beylerbeyi",
    "MUHTEL??F ??SK.": "??sk??dar",
    "A.KAVA??I": "Anadolu Kava????",
    "R.KAVA??I - SARIYER": "Rumeli Kava????",
    "K??????K SU": "K??????ksu",
}
for pat, repl in repl_dict.items():
    dataset.loc[:, "has-line"] = dataset.loc[:, "has-line"].str.replace(
        pat, repl, regex=True
    )

# fix value formatting of the "has-line" column
dataset.loc[:, "has-line"] = dataset.loc[:, "has-line"].str.replace(
    r"(\w)-(\w)", lambda x: (x.group(1) + " - " + x.group(2)), regex=True
)
# fix 'shape-data' formatting
# do this by writing to WKT and getting WKT expression back
wkt_shape_data = [dataset["shape-data"].apply(lambda x: try_wkt_conversion(x))]

# sort by 'terminal-name' columns, add unique id, and reorder columns
dataset = dataset.sort_values(by="terminal-name").reset_index(drop=True)
dataset["id"] = [i for i in range(1, len(dataset) + 1)]
dataset = dataset.reindex(columns=["id", "terminal-name", "shape-data", "has-line"])

# separate out the 'ferry-terminals' dataset from the 'terminals-lines' dataset
datasets["terminals-lines"] = dataset.loc[:, ["id", "terminal-name", "has-line"]]
dataset = dataset.drop("has-line", axis=1)

# re-write the dataset into the dict
datasets["ferry-terminals"] = dataset

# --- clean 'ferry-lines-geoloc.csv' ---
dataset = datasets["ferry-lines"]

# filter by only '??ehir hatlar??'
dataset = dataset.loc[
    dataset["isim_kurum"].str.contains("??ehir Hatlar?? Turizm ve Tic. San. A??.")
]

# drop unnecessary columns
dataset = dataset.loc[:, ["line-name", "shape-data"]]

# fix values in the "line-name" column
# extending the previous 'repl_dict' since it hasn't been recycled yet.
repl_dict["Bosphorusdan Geli??"] = "From Bosph. to South"
repl_dict["Bosphorusa Gidi??"] = "From South to Bosph."
repl_dict["U??ramas??z"] = "Not Visited"
repl_dict["K??nal??ada"] = "K??nal??ada"
repl_dict["Uzun"] = "Long"
repl_dict["K??sa"] = "Short"
repl_dict["Turu"] = "Tour"
repl_dict["??stinye - ??ubuklu (Car Ferry)"] = "??stinye - ??ubuklu Car Ferry Line"
repl_dict["??sk??dar - Karak??y - Emin??n?? - Ey??p (Hali?? Line)"] = "$1"
repl_dict["From Bosph. to South"] = "Bosphorus Line"
repl_dict["From South to Bosph."] = "Bosphorus Line"
for pat, repl in repl_dict.items():
    dataset.loc[:, "line-name"] = dataset.loc[:, "line-name"].str.replace(
        pat, repl, regex=True
    )

# fix value formatting of the "line-name" column
dataset.loc[:, "line-name"] = dataset.loc[:, "line-name"].str.replace(
    r"(\w)-(\w)", lambda x: (x.group(1) + " - " + x.group(2)), regex=True
)

# fix 'shape-data' formatting
dataset["shape-data"] = (
    dataset["shape-data"].str.replace(";", ",").apply(lambda x: try_wkt_conversion(x))
)
# drop NaN values
dataset = dataset.dropna()

# merge lines with multiple representations into one
for line_name in ["Adalar - Bostanc??", "Bosphorus Line"]:
    subset = dataset.loc[dataset["line-name"] == line_name, "shape-data"]
    multi_line = []
    for value in subset.values:
        multi_line.append(loads(value))
    multi_line = geometry.MultiLineString(multi_line)
    merged_line = ops.linemerge(multi_line)
    dataset.loc[dataset["line-name"] == line_name, "shape-data"] = merged_line.wkt

dataset = dataset.groupby("line-name").first()

# Reset index and give a unique ID to all lines
dataset = dataset.reset_index()
dataset["id"] = [i for i in range(1, len(dataset["line-name"]) + 1)]

# reorder and sort by 'line-name' columns
dataset = dataset.reindex(columns=["id", "line-name", "shape-data"]).sort_values(
    by="line-name"
)

# re-write the dataset into the dict
datasets["ferry-lines"] = dataset

# --- clean 'terminals-lines' dataframe ---
dataset = datasets["terminals-lines"]

# explode 'has-line' column
nested_mask = dataset["has-line"].str.contains("/")
dataset.loc[nested_mask, "has-line"] = dataset.loc[nested_mask, "has-line"].str.split(
    "/"
)
dataset = dataset.explode(column="has-line")

# fix formatting errors caused by unnesting
dataset["has-line"] = dataset["has-line"].str.strip()

# join with 'ferry-lines' dataset
dataset = (
    pd.merge(
        left=dataset,
        right=datasets["ferry-lines"].loc[:, ["line-name", "id"]],
        how="left",
        left_on="has-line",
        right_on="line-name",
    )
    .drop("line-name", axis=1)
    .dropna()
)

# rename columns
dataset = dataset.rename({"id_x": "terminal-id", "id_y": "line-id"}, axis=1)

# fix minor data type problems
dataset["line-id"] = dataset["line-id"].astype(int)

# re-write the dataset into the dict
datasets["terminals-lines"] = dataset

# --- clean 'passengers-per-ferry-line_2020.csv' ---
dataset = datasets["trips-per-ferry-line"]

# fix 'line-name' values
repl_dict["MUHTEL??F"] = "Muhtelif"
repl_dict["R??NG"] = "Ring"
repl_dict["PA??ABAH??E"] = "Pa??abah??e"
repl_dict["??STANBUL"] = "??stanbul"
repl_dict["G??D???? GEL????"] = "Gidi?? Geli??"
repl_dict["KASIMPA??A"] = "Kas??mpa??a"
repl_dict["SEFERLER??"] = "Seferleri"
repl_dict["EM??RGAN"] = "Emirgan"
repl_dict["HEYBEL??ADA"] = "Heybeliada"
repl_dict["??SK"] = "??sk??dar"

for pat, repl in repl_dict.items():
    dataset.loc[:, "line-name"] = dataset.loc[:, "line-name"].str.replace(
        pat.upper(),
        repl,
        regex=True,
    )

# fix data type of "n-trips"
dataset["n-trips"] = (
    dataset["n-trips"]
    .astype(str)
    .str.rstrip("0")
    .str.replace(".", "", regex=True)
    .astype(int)
)

# fix some 'n-trips' values manually
dataset.loc[dataset["n-trips"] == 449, "n-trips"] = 4490
dataset.loc[dataset["n-trips"] == 197, "n-trips"] = 1970

# re-write the dataset into the dict
datasets["trips-per-ferry-line"] = dataset

# --- clean 'transportation-load_2020xx.csv's ---
dataset = datasets["transportation-load"]

# filter rows
dataset = dataset.loc[dataset["TRANSPORT_TYPE_ID"] == 3, :]

# calculate true sum of 'NUMBER_OF_PASSENGER' & drop unnecessary columns
dataset = dataset.groupby("DATE_TIME").agg({"NUMBER_OF_PASSENGER": sum}).reset_index()

# reformat 'date_time' column
# can be done by converting to DT object
dataset["DATE_TIME"] = pd.to_datetime(dataset["DATE_TIME"])

# fill non-existent days with NaN
whole_year = pd.date_range(
    start="1/1/2020 00:00:00", end="31/12/2020 23:00:00", freq="1H"
)
missing_dates = whole_year[~(whole_year.isin(dataset["DATE_TIME"]))]

missing_dates = pd.DataFrame(data=missing_dates, columns=["DATE_TIME"])
missing_dates["NUMBER_OF_PASSENGER"] = [np.nan for i in range(0, len(missing_dates))]

dataset = pd.concat([dataset, missing_dates], ignore_index=True)

# expand 'DATE_TIME' column to diff. columns
dataset["day"] = dataset["DATE_TIME"].dt.day.astype(int)
dataset["month"] = dataset["DATE_TIME"].dt.month.astype(int)
dataset["year"] = dataset["DATE_TIME"].dt.year.astype(int)
dataset["hour"] = dataset["DATE_TIME"].dt.hour.astype(int)

# drop columns, change column order and rename columns
dataset = (
    dataset.sort_values(by="DATE_TIME", axis=0, ascending=True, ignore_index=True)
    .drop(["DATE_TIME"], axis=1)
    .reindex(columns=["day", "month", "year", "hour", "NUMBER_OF_PASSENGER"])
    .rename({"NUMBER_OF_PASSENGER": "n-passengers"}, axis=1)
)

# rewrite the dataset back into the dict
datasets["transportation-load"] = dataset

# --- clean 'automated-weather-stations-geoloc.csv' ---
dataset = datasets["automated-weather-stations"]
dataset = list(dataset.index[:10].values)  # Need this because it turns out weird
dataset = pd.DataFrame(dataset, columns=["header", "sensor-name", "shape-data"])

# split out the 'shape-data' column to two temp columns
dataset["shape-data"] = dataset["shape-data"].str.split(",")

for i, col_label in enumerate(["TEMP_x", "TEMP_y"]):
    dataset[col_label] = dataset["shape-data"].apply(lambda x: x[i]).str.strip()

# turn degrees-minutes notation of 'shape-data' to degrees notation
for col_label in ["TEMP_x", "TEMP_y"]:
    dataset[col_label] = dataset[col_label].apply(
        lambda x: convert_coord(x, "degrees_minutes", "degrees")
    )

# recreate the 'shape-data' column using WKT notation
points = []
for x, y in zip(dataset["TEMP_x"].values, dataset["TEMP_y"].values):
    point = geometry.Point((x, y)).wkt
    points.append(point)
dataset["shape-data"] = points

# drop unnecessary columns
dataset = dataset.loc[:, ["sensor-name", "shape-data"]]

# sort by 'sensor-name' and give all sensors a unique id
dataset = dataset.sort_values(by="sensor-name")
dataset["id"] = [i for i in range(1, len(dataset) + 1)]

# reorder columns
dataset = dataset.reindex(columns=["id", "sensor-name", "shape-data"])

# rewrite the dataset back into the dict
datasets["automated-weather-stations"] = dataset

# --- clean 'icing-sensors.geoloc.csv' ---
dataset = datasets["icing-sensors"]
dataset = (
    dataset.loc[:, ["station-header", "station-name_1"]]
    .rename({"station-header": "sensor-name", "station-name_1": "shape-data"}, axis=1)
    .reset_index(drop=True)
)
# split out the 'shape-data' column to two temp columns
dataset["shape-data"] = dataset["shape-data"].str.split(",")

for i, col_label in enumerate(["TEMP_x", "TEMP_y"]):
    dataset[col_label] = dataset["shape-data"].apply(lambda x: x[i]).str.strip()

# turn degrees-minutes-seconds notation of 'shape-data' to degrees notation
for col_label in ["TEMP_x", "TEMP_y"]:
    dataset[col_label] = dataset[col_label].apply(
        lambda x: convert_coord(x, "degrees_minutes_seconds", "degrees")
    )

# recreate the 'shape-data' column using WKT notation
points = []
for x, y in zip(dataset["TEMP_x"].values, dataset["TEMP_y"].values):
    point = geometry.Point((x, y)).wkt
    points.append(point)
dataset["shape-data"] = points


# sort by 'sensor-name' and give all sensors a unique id
dataset = dataset.sort_values(by="sensor-name")
dataset["id"] = [i for i in range(1, len(dataset) + 1)]

#  reorder columns
dataset = dataset.reindex(columns=["id", "sensor-name", "shape-data"])

# rewrite the dataset back into the dict
datasets["icing-sensors"] = dataset


# --- merge 'automated-weather-stations' and 'icing-sensors' ---
dataset = pd.concat(
    objs=[datasets["automated-weather-stations"], datasets["icing-sensors"]],
    ignore_index=True,
)

# Fix 'sensor-name' string formatting issues
dataset["sensor-name"] = dataset["sensor-name"].str.lstrip()

# sort by 'sensor-name' and give all sensors a unique id
dataset = dataset.sort_values(by="sensor-name", ascending=True).reset_index(drop=True)
dataset["id"] = [i for i in range(1, len(dataset) + 1)]

# write the dataset into the dict
datasets["weather-sensors"] = dataset

# --- clean 'observations-load_2020xx.csv's ---
dataset = datasets["weather-observations"]

# drop unnecessary columns
dataset = dataset.loc[
    :,
    [
        "DATE_TIME",
        "AVERAGE_TEMPERATURE",
        "AVERAGE_HUMIDITY",
        "AVERAGE_WIND",
        "AVERAGE_DIRECTIONOFWIND",
        "AVERAGE_PRECIPITATION",
    ],
]

# fix 'DATE_TIME' column value format discrepancies
# can be done by converting to DT object
dataset["DATE_TIME"] = pd.to_datetime(dataset["DATE_TIME"])

# replace illogical values in numerical columns with NaN
for col in [
    "AVERAGE_HUMIDITY",
    "AVERAGE_WIND",
    "AVERAGE_PRECIPITATION",
    "AVERAGE_DIRECTIONOFWIND",
]:
    illogical_mask = dataset[col] < 0
    dataset.loc[illogical_mask, col] = np.nan

# group by 'DATE_TIME' to get an avg of different stations
dataset = (
    dataset.groupby("DATE_TIME")
    .agg(
        {
            "AVERAGE_TEMPERATURE": "mean",
            "AVERAGE_HUMIDITY": "mean",
            "AVERAGE_WIND": "mean",
            "AVERAGE_DIRECTIONOFWIND": "mean",
            "AVERAGE_PRECIPITATION": "mean",
        }
    )
    .reset_index()
)

# fill non-existent days with NaN
whole_year = pd.date_range(
    start="1/1/2020 00:00:00", end="31/12/2020 23:00:00", freq="1H"
)
missing_dates = whole_year[~(whole_year.isin(dataset["DATE_TIME"]))]

missing_dates = pd.DataFrame(data=missing_dates, columns=["DATE_TIME"])
for col_header in [
    "AVERAGE_TEMPERATURE",
    "AVERAGE_HUMIDITY",
    "AVERAGE_WIND",
    "AVERAGE_DIRECTIONOFWIND",
    "AVERAGE_PRECIPITATION",
]:
    missing_dates[col_header] = [np.nan for i in range(0, len(missing_dates))]

dataset = pd.concat([dataset, missing_dates], ignore_index=True)

# expand 'DATE_TIME' column to diff. columns
dataset["day"] = dataset["DATE_TIME"].dt.day.astype(int)
dataset["month"] = dataset["DATE_TIME"].dt.month.astype(int)
dataset["year"] = dataset["DATE_TIME"].dt.year.astype(int)
dataset["hour"] = dataset["DATE_TIME"].dt.hour.astype(int)

# sort date_time and then clean up columns
dataset = (
    dataset.sort_values(by="DATE_TIME", ascending=True)
    .drop("DATE_TIME", axis=1)
    .rename(
        {
            "AVERAGE_TEMPERATURE": "avg-temp",
            "AVERAGE_HUMIDITY": "avg-humidity",
            "AVERAGE_WIND": "avg-wind",
            "AVERAGE_DIRECTIONOFWIND": "avg-winddir",
            "AVERAGE_PRECIPITATION": "avg-precip",
        },
        axis=1,
    )
    .reindex(
        columns=[
            "day",
            "month",
            "year",
            "hour",
            "avg-temp",
            "avg-humidity",
            "avg-precip",
            "avg-wind",
            "avg-winddir",
        ]
    )
)

# rewrite to datasets dictionary
datasets["weather-observations"] = dataset

# --- export data ---
for dataset_name in [
    "ferry-terminals",
    "ferry-lines",
    "terminals-lines",
    "trips-per-ferry-line",
    "transportation-load",
    "weather-sensors",
    "weather-observations",
]:
    path = Path("data/cleaned/{}.csv".format(dataset_name))
    datasets[dataset_name].to_csv(
        path_or_buf=path, sep=",", index=False, encoding="utf-8-sig"
    )
