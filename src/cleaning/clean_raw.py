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
        "headers": ["year", "line-name", "n_trips"],
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
dataset = dataset.loc[dataset["turu_iskele"] == "IDO Þehir Hatlarý", :]

# drop unnecessary columns
dataset = dataset.drop(["globalid", "turu_iskele"], axis=1)

# fix values in the 'terminal-name' column
# code here is extremely verbose and not using any regex to fix commonly
# occuring patterns on purpose because I am using real-life knowledge to
# correct data quality.
repl_dict = {
    "Anadolu Hisarý ÞH.": "Anadolu Hisarı",
    "Kabataþ ÞH.": "Kabataş",
    "Kadýköy-Beþiktaþ-Adalar ÞH.": "Kadıköy - Beşiktaş - Adalar",
    "Kandilli ÞH.": "Kandilli",
    "Kanlýca ÞH.": "Kanlıca",
    "Karaköy ÞH.": "Karaköy",
    "Kasýmpaþa ÞH.": "Kasımpaşa",
    "Kuzguncuk ÞH.": "Kuzguncuk",
    "Küçüksu ÞH.": "Küçüksu",
    "Kýnalýada ÞH.": "Kınalıada",
    "Ortaköy ÞH.": "Ortaköy",
    "Paþabahçe ÞH.": "Paşabahçe",
    "Rumeli Kavaðý ÞH.": "Rumeli Kavağı",
    "Sarýyer ÞH.": "Sarıyer",
    "Sedef Adasý ÞH.": "Sedef Adası",
    "Sütlüce ÞH.": "Sütlüce",
    "Yeni Kadýköy ÞH.": "Yeni Kadıköy",
    "Yeniköy ÞH.": "Yeniköy",
    "Çengelköy ÞH.": "Çengelköy",
    "Çubuklu ÞH.": "Çubuklu",
    "Çubuklu ÞH. (Arabalý Vapur)": "Çubuklu Car Ferry Terminal",
    "Üsküdar ÞH.": "Üsküdar",
    "Ýstinye ÞH.": "İstinye",
    "Kadýköy-Beþiktaþ ÞH.": "Kadıköy - Beşiktaş",
    "Heybeliada ÞH.": "Heybeliada",
    "Anadolu Kavaðý ÞH.": "Anadolu Kavağı",
    "Haydarpaþa ÞH.": "Haydarpaşa",
    "Arnavutköy ÞH.": "Arnavutköy",
    "Ayvansaray ÞH.": "Ayvansaray",
    "Balat ÞH.": "Balat",
    "Bebek ÞH.": "Bebek",
    "Beykoz ÞH.": "Beykoz",
    "Beylerbeyi ÞH.": "Beylerbeyi",
    "Beþiktaþ-Kadýköy ÞH.": "Beşiktaş - Kadıköy",
    "Beþiktaþ-Üsküdar ÞH.": "Beşiktaş - Üsküdar",
    "Bostancý ÞH.": "Bostancı",
    "Burgazada ÞH.": "Burgazada",
    "Büyükada ÞH.": "Büyükada",
    "Büyükdere ÞH.": "Büyükdere",
    "Eminönü Camlý Ýskele ÞH.": "Eminönü Small Terminal",
    "Eminönü-Boðaz ÞH.": "Eminönü - Bosphorus",
    "Eminönü-Haliç ÞH.": "Eminönü Haliç",
    "Eminönü-Kadýköy ÞH.": "Eminönü - Kadıköy",
    "Eminönü-Üsküdar ÞH.": "Eminönü - Üsküdar",
    "Emirgan ÞH.": "Emirgan",
    "Eyüp ÞH.": "Eyüp",
    "Fener ÞH.": "Fener",
    "Hasköy ÞH.": "Hasköy",
    "Ýstinye ÞH. (Arabalý Vapur)": "İstinye Car Ferry Terminal",
}
dataset = dataset.replace(repl_dict)

# fix values in the 'has-line' column
repl_dict = {
    "Hattý": "Line",
    "Boðaz": "Bosphorus",
    "Kabataþ": "Kabataş",
    "Kadýköy": "Kadıköy",
    "Beþiktaþ": "Beşiktaş",
    "BEÞÝKTAÞ": "Beşiktaş",
    "MUHTELÝF": "Muhtelif",
    "Sarýyer": "Sarıyer",
    "Kavaðý": "Kavağı",
    "Ýstinye": "İstinye",
    "Arabalý Vapur": "Car Ferry",
    "Bostancý": "Bostancı",
    "Adasý": "Adası",
    "Haydarpaþa": "Haydarpaşa",
    "Bostancý": "Bostancı",
    "EMÝNÖNÜ": "Eminönü",
    "ÝSTÝNYE": "İstinye",
    "EMÝRGAN": "Emirgan",
    "BEYLERBEYÝ": "Beylerbeyi",
    "MUHTELÝF ÝSK.": "Üsküdar",
    "A.KAVAÐI": "Anadolu Kavağı",
    "R.KAVAÐI - SARIYER": "Rumeli Kavağı",
    "KÜÇÜK SU": "Küçüksu",
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

# filter by only 'şehir hatları'
dataset = dataset.loc[
    dataset["isim_kurum"].str.contains("Þehir Hatlarý Turizm ve Tic. San. AÞ.")
]

# drop unnecessary columns
dataset = dataset.loc[:, ["line-name", "shape-data"]]

# fix values in the "line-name" column
# extending the previous 'repl_dict' since it hasn't been recycled yet.
repl_dict["Bosphorusdan Geliþ"] = "From Bosph. to South"
repl_dict["Bosphorusa Gidiþ"] = "From South to Bosph."
repl_dict["Uðramasýz"] = "Not Visited"
repl_dict["Kýnalýada"] = "Kınalıada"
repl_dict["Uzun"] = "Long"
repl_dict["Kýsa"] = "Short"
repl_dict["Turu"] = "Tour"
repl_dict["İstinye - Çubuklu (Car Ferry)"] = "İstinye - Çubuklu Car Ferry Line"
repl_dict["Üsküdar - Karaköy - Eminönü - Eyüp (Haliç Line)"] = "$1"
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
for line_name in ["Adalar - Bostancı", "Bosphorus Line"]:
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
repl_dict["MUHTELÝF"] = "Muhtelif"
repl_dict["RÝNG"] = "Ring"
repl_dict["PAÞABAHÇE"] = "Paşabahçe"
repl_dict["ÝSTANBUL"] = "İstanbul"
repl_dict["GÝDÝÞ GELÝÞ"] = "Gidiş Geliş"
repl_dict["KASIMPAÞA"] = "Kasımpaşa"
repl_dict["SEFERLERÝ"] = "Seferleri"
repl_dict["EMÝRGAN"] = "Emirgan"
repl_dict["HEYBELÝADA"] = "Heybeliada"
repl_dict["ÝSK"] = "Üsküdar"

for pat, repl in repl_dict.items():
    dataset.loc[:, "line-name"] = dataset.loc[:, "line-name"].str.replace(
        pat.upper(),
        repl,
        regex=True,
    )

# fix data type of "n_trips"
dataset["n_trips"] = (
    dataset["n_trips"]
    .astype(str)
    .str.rstrip("0")
    .str.replace(".", "", regex=True)
    .astype(int)
)

# fix some 'n_trips' values manually
dataset.loc[dataset["n_trips"] == 449, "n_trips"] = 4490
dataset.loc[dataset["n_trips"] == 197, "n_trips"] = 1970

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
    .rename({"NUMBER_OF_PASSENGER": "n_passengers"}, axis=1)
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
            "AVERAGE_DIRECTIONOFWIND": "avg-windir",
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
            "avg-windir",
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
