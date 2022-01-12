from pathlib import Path


import pandas as pd

# Import data
import_dicts = [
    {
        "tag": "ferry-terminals",
        "path": Path("data/raw/geolocation/ferry-terminals-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ";",
        "headers": ["terminal-name", "has-line", "turu_iskele", "globalid", "geometry"],
        "skiprows": 0,
    },
    {
        "tag": "ferry-lines",
        "path": Path("data/raw/geolocation/ferry-lines-geoloc.csv"),
        "encoding": "utf-8",
        "sep": ";",
        "headers": [
            "line_name",
            "isim_kurum",
            "tur_hat",
            "website",
            "globalid",
            "geometry",
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
    "Çubuklu ÞH. (Arabalý Vapur)": "Çubuklu Car Ferry",
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
    "Eminönü Camlý Ýskele ÞH.": "Eminönü Small Pier",
    "Eminönü-Boðaz ÞH.": "Eminönü - Boğaz",
    "Eminönü-Haliç ÞH.": "Eminönü Haliç",
    "Eminönü-Kadýköy ÞH.": "Eminönü - Kadıköy",
    "Eminönü-Üsküdar ÞH.": "Eminönü - Üsküdar",
    "Emirgan ÞH.": "Emirgan",
    "Eyüp ÞH.": "Eyüp",
    "Fener ÞH.": "Fener",
    "Hasköy ÞH.": "Hasköy",
    "Ýstinye ÞH. (Arabalý Vapur)": "İstinye Car Ferry",
}
dataset = dataset.replace(repl_dict)
# fix values in the 'has-line' column
repl_dict = {
    "Hattý": "Line",
    "Boðaz": "Boğaz",
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
    dataset.loc[:, "has-line"] = dataset.loc[:, "has-line"].str.replace(pat, repl)

# --- clean 'ferry-lines-geoloc.csv' ---
dataset = datasets["ferry-lines"]
# Fix mess from CSV parsing & drop unnecessary rows at once
# dataset = dataset.loc[:, ["line_name", "geometry"]]
print(dataset["geometry"])
