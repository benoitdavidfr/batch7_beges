import os
import pandas as pd
import math
import datetime

names_to_replace = {
    "CLIO IV": "CLIO 4",
    "CLIO III": "CLIO 3",
    "MÉGANE": "MEGANE",
    "ZOÉ": "ZOE",
}


def clean_modele(modele):
    modele = str(modele).upper()
    if modele in names_to_replace.keys():
        modele = names_to_replace.get(modele)
    return modele


def clean_date(date_value):
    if date_value == math.nan or date_value == "00/01/00" or date_value is None:
        date_value = datetime.datetime.today()
    return date_value


def main():
    data_xls = pd.read_excel("C:/Users/Artus/batch7_beges/data/raw/odrive/odrive.xlsx", index_col=None)
    data_xls["Modèle"] = list(map(clean_modele, data_xls["Modèle"]))
    data_xls["Date relevé"] = list(map(clean_date, data_xls["Date relevé"]))
    data_xls["Date 1ère mise en circulation"] = list(map(clean_date, data_xls["Date 1ère mise en circulation"]))
    data_xls["Total années cirulation"] = (data_xls["Date relevé"] - data_xls["Date 1ère mise en circulation"]).astype(
        "timedelta64[D]"
    ) / 365
    data_xls["km parcours par an"] = (
        list(map(int, data_xls["Dernier relevé km"].fillna(0))) / data_xls["Total années cirulation"]
    )
    data_xls["Emissions (g/an)"] = data_xls["km parcours par an"] * data_xls["CO2 (g/km)"]
    data_xls.to_csv("C:/Users/Artus/batch7_beges//data/cleaned/odrive.csv", encoding="utf-8")


if __name__ == "__main__":
    main()
