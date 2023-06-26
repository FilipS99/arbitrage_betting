import pandas as pd
import numpy as np

from synonyms_polish_football import synonyms_polish_football
from synonyms_finnish_football import synonyms_finnish_football
from synonyms_brazilian_football import synonyms_brazilian_football
from synonyms_rugby import synonyms_rugby
from synonyms_ufc import synonyms_ufc
from synonyms_tennis import synonyms_tennis


def rename_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    # replace in team names
    replace_list = [
                    ['baraż / PF / Rozszerzona oferta LIVE', ''],
                    ['baraż / PF', ''],
                    ['baraż / Finał', ''],
                    ['(HITDNIA)', ''],
                    [' ', ''], 
                    ['-', ''], 
                    ['/', '']
                   ]
    for replace in replace_list:
        df[['team_1','team_2']] = df[['team_1','team_2']].replace(replace[0], replace[1], regex = True)

    # upper
    df['team_1'] = df['team_1'].str.upper()
    df['team_2'] = df['team_2'].str.upper()

    df.loc[df['category'] == 'polish football'] = df.loc[df['category'] == 'polish football'].replace(synonyms_polish_football)
    df.loc[df['category'] == 'finnish football'] = df.loc[df['category'] == 'finnish football'].replace(synonyms_finnish_football)
    df.loc[df['category'] == 'brazilian football'] = df.loc[df['category'] == 'brazilian football'].replace(synonyms_brazilian_football)
    df.loc[df['category'] == 'rugby'] = df.loc[df['category'] == 'rugby'].replace(synonyms_rugby)
    df.loc[df['category'] == 'ufc'] = df.loc[df['category'] == 'ufc'].replace(synonyms_ufc)
    df.loc[df['category'] == 'tennis'] = df.loc[df['category'] == 'tennis'].replace(synonyms_tennis)
    

    # df = df.replace({'team_1': synonyms,
    #                 'team_2': synonyms})

    return df


# testing input
# df = pd.read_excel(
#     'D:\\moje\\python_projects\\arbitrage_betting\\output\\20230605_210608_scraped.xlsx')
# rename_synonyms(df)

# print(df)
