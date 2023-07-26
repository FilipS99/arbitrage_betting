import pandas as pd
import numpy as np
import re

from synonyms_polish_football import synonyms_polish_football
from synonyms_finnish_football import synonyms_finnish_football
from synonyms_brazilian_football import synonyms_brazilian_football
from synonyms_rugby import synonyms_rugby
from synonyms_ufc import synonyms_ufc
from synonyms_tennis import synonyms_tennis


def rename_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    # delete from team names
    patterns = [r'\(K\)',
                r'\(K\)',
                r'\(WOM\)',
                r'\(KOBIETY\)',
                r'\(HIT DNIA\)',
                r'baraż / PF / Rozszerzona oferta LIVE',
                r'\(najwyższe kursy, 0% marży!\)',
                r'baraż / PF',
                r'baraż / Finał',
                r'U\d{2}',
                r'\[K\]',
                r'\[WOM\]',
                r'-',
                r'/',
                r'"',
                r"'",
                r',',
                r' ']

    for pattern in patterns:
        df['team_1'] = df['team_1'].str.replace(
            pattern, '', flags=re.IGNORECASE, regex=True)
        df['team_2'] = df['team_2'].str.replace(
            pattern, '', flags=re.IGNORECASE, regex=True)

    # upper
    df['team_1'] = df['team_1'].str.upper()
    df['team_2'] = df['team_2'].str.upper()

    df.loc[df['category'] == 'polish football'] = df.loc[df['category']
                                                         == 'polish football'].replace(synonyms_polish_football)
    df.loc[df['category'] == 'finnish football'] = df.loc[df['category']
                                                          == 'finnish football'].replace(synonyms_finnish_football)
    df.loc[df['category'] == 'brazilian football'] = df.loc[df['category']
                                                            == 'brazilian football'].replace(synonyms_brazilian_football)
    df.loc[df['category'] == 'rugby'] = df.loc[df['category']
                                               == 'rugby'].replace(synonyms_rugby)
    df.loc[df['category'] == 'ufc'] = df.loc[df['category']
                                             == 'ufc'].replace(synonyms_ufc)
    df.loc[df['category'] == 'tennis'] = df.loc[df['category']
                                                == 'tennis'].replace(synonyms_tennis)

    return df


# testing input
# df = pd.read_excel(
#     'D:\\moje\\python_projects\\arbitrage_betting\\output\\20230605_210608_scraped.xlsx')
# rename_synonyms(df)

# print(df)
