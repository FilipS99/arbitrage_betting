import pandas as pd
import numpy as np


def rename_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    # replace every space
    df = df.replace(' ', '', regex=True)

    # upper
    df['team_1'] = df['team_1'].str.upper()
    df['team_2'] = df['team_2'].str.upper()

    # dictionary of synonym replacements
    synonyms = {
        'G.ZABRZE': 'GÓRNIKZABRZE',
        'GÓRNIKZ.': 'GÓRNIKZABRZE',
        'Z.LUBLIN': 'ZAGŁĘBIELUBLIN',
        'ZAGŁĘBIEL.': 'ZAGŁĘBIELUBLIN',
        'LUBLIN': 'ZAGŁĘBIELUBLIN',
        'TYCHY': 'GKSTYCHY',
        'ARKA': 'ARKAGDYNIA',
        'SKRACZ.': 'SKRACZĘSTOCHOWA',
        'CHOJNICE': 'CHOJNICZANKACHOJNICE',
        'W.KRAKÓW': 'WISŁAKRAKÓW',
        'NIECIECZA': 'TERMALICANIECIECZA',
        'BRUK-BETTERMALICANIECIECZA': 'TERMALICANIECIECZA',
        'TERMALICABRUK-B.': 'TERMALICANIECIECZA',
        'OPOLE': 'ODRAOPOLE',
        'CHOJNICZANKA': 'CHOJNICZANKACHOJNICE',
        'CHOJNICZANKACHO.': 'CHOJNICZANKACHOJNICE',
        'MKSCHOJNICZANKACHOJNICE': 'CHOJNICZANKACHOJNICE',
        'PUSZCZANIEPOŁOM.': 'PUSZCZANIEPOŁOMICE',
        'NIEPOŁOMICE': 'PUSZCZANIEPOŁOMICE',
        'SOSNOWIEC': 'ZAGŁĘBIESOSNOWIEC',
        'ZAGŁĘBIESOSNOWI.': 'ZAGŁĘBIESOSNOWIEC',
        'CWKSRESOVIA': 'RESOVIA',
        'RESOVIARZESZÓW': 'RESOVIA',
        'PODBESKIDZIEBIE.': 'PODBESKIDZIE',
        'TSPODBESKIDZIEBIELSKO-BIAŁA': 'PODBESKIDZIE',
        'ŁĘCZNA': 'GÓRNIKŁĘCZNA',
        'G.ŁĘCZNA': 'GÓRNIKŁĘCZNA',
        'SANDECJA': 'SANDECJANOWYSĄCZ',
        'CHORZÓW': 'RUCHCHORZÓW',
        'GŁOGÓW': 'CHROBRYGŁOGÓW',
        'SANDECJANOWYSĄ.': 'SANDECJANOWYSĄCZ'
    }

    df = df.replace({"team_1": synonyms,
                    "team_2": synonyms})

    # print(df)

    return df


# testing input
# df = pd.read_excel(
#     'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\20230527_144257.xlsx')[["team_1",  "team_2"]]
# rename_synonyms(df)

# print(df)
