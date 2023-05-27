import pandas as pd
import numpy as np


def rename_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    # replace every space
    df = df.replace(' ', '', regex=True)

    # dictionary of synonym replacements
    synonyms = {
        'G.Zabrze': 'GórnikZabrze',
        'GórnikZ.': 'GórnikZabrze',
        'ZagłębieLublin': 'Z.Lublin',
        'ZagłębieL.': 'ZagłębieLublin',
        'Lublin': 'ZagłębieLublin'
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
