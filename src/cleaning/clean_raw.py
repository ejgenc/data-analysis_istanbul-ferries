from pathlib import Path

import pandas as pd

from src.helper_functions import check_line_validity, check_point_validity

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
dataset.loc[:, "shape-data"] = (
    dataset.loc[:, "shape-data"]
    .str.replace("[POINT()]", "", regex=True)
    .str.strip()
    .str.replace(" ", "|", regex=True)
)
# sort by 'terminal-name' columns, add unique id, and reorder columns
dataset = dataset.sort_values(by="terminal-name").reset_index(drop=True)
dataset["id"] = [i for i in range(1, len(dataset) + 1)]
dataset = dataset.reindex(columns=["id", "terminal-name", "shape-data", "has-line"])
# separate out the 'ferry-terminals' dataset from the 'terminals-lines' dataset
datasets["terminals-lines"] = dataset.loc[:, ["id", "terminal-name", "has-line"]]
dataset = dataset.drop("has-line", axis=1)
# drop the "has-line" column
# re-write the dataset into the dict
datasets["ferry-terminals"] = dataset

# # --- clean 'ferry-lines-geoloc.csv' ---
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
dataset.loc[:, "shape-data"] = (
    dataset.loc[:, "shape-data"]
    .str.replace("[POINT()LINESTRINGMULTILINESTRING]", "", regex=True)
    .str.strip()
    .str.replace(" ", "|", regex=True)
)
# drop any rows whose 'shape-data' is not valid.
valid_geom_mask = []
mask_base = dataset["shape-data"]
mask_base = (mask_base.str.split(";")).values
for data_list in mask_base:
    valid = True
    try:
        line_points = []
        for data in data_list:
            data = data.lstrip("|").split("|")
            try:
                check_point_validity(float(data[0]), float(data[1]))
            except Exception:
                raise Exception
            line_points.append((float(data[0]), float(data[1])))
        try:
            check_line_validity(line_points)
        except Exception:
            raise Exception
    except Exception:
        valid = False
    finally:
        valid_geom_mask.append(valid)

dataset = dataset.loc[valid_geom_mask, :]
# merge the rows that have the same line name
dataset = dataset.groupby("line-name").agg({"shape-data": " ".join}).reset_index()
# drop 'Adalar Bostancı' and 'Bosphorus Line' lines because they just don't work
for line_name in ["Adalar - Bostancı", "Bosphorus Line"]:
    dataset = dataset.loc[dataset["line-name"] != line_name, :]
# dataset = dataset.loc[,?
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
print(datasets["terminal-lines"])
