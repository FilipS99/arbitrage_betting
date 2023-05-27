import numpy as np
import pandas as pd


df = pd.read_excel(
    'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\20230527_144257.xlsx')

# df = df.groupby(["team_1",  "team_2"])
# df['ratio'] = 1./df["stake_1_wins"] + 1. / \
#     df["stake_draw"] + 1./df["stake_2_wins"]

df_agg = df.groupby(["team_1",  "team_2"]).max()

df['ratio'] = 1./df["stake_1_wins"] + 1. / \
    df["stake_draw"] + 1./df["stake_2_wins"]

# TODO uwzglednic url z z najlepszą stawką dla każdej opcji

print(df)
