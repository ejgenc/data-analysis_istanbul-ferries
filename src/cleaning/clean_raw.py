from pathlib import Path

import pandas as pd
from shapely import geometry, ops
from shapely.wkt import loads

from src.helper_functions import try_wkt_conversion

# Import data
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
]
datasets = {}
for import_dict in import_dicts:
    datasets[import_dict["tag"]] = pd.read_csv(
        import_dict["path"],
        encoding=import_dict["encoding"],
        sep=import_dict["sep"],
        names=import_dict["headers"],
        skiprows=import_dict["skiprows"],
    )


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
    "Sarýyer": "Sarıyer",
    "Kavaðý": "Kavağı",
    "Ýstinye": "İstinye",
    "Arabalý Vapur": "Car Ferry",
    "Bostancý": "Bostancı",
    "Adasý": "Adası",
    "Haydarpaþa": "Haydarpaşa",
    "Bostancý": "Bostancı",
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
