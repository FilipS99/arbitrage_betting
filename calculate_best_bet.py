import numpy as np
import pandas as pd

from rename_synonyms import rename_synonyms


df = pd.read_excel(
    'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\20230527_204748.xlsx')

df = rename_synonyms(df)

print(df)
print(df[["team_1",  "team_2", 'stake_1_wins', 'url']])
print(df[["team_1",  "team_2", 'stake_draw', 'url']])
print(df[["team_1",  "team_2", 'stake_2_wins', 'url']])

df = df.groupby(["team_1",  "team_2"]).max()

# df['ratio'] = 1./df["stake_1_wins"] + 1. / \
#     df["stake_draw"] + 1./df["stake_2_wins"]

# # TODO uwzglednic url z z najlepszą stawką dla każdej opcji

# print(df)


# Calculate the sum of implied probabilities
df['total_implied_prob'] = 1 / df['stake_1_wins'] + \
    1 / df['stake_draw'] + 1 / df['stake_2_wins']

# Total amount to bet
amount = 1000

# Calculate tbet amounts
df['bet_win_1'] = amount / \
    (1+df['stake_1_wins']/df['stake_draw'] +
     df['stake_1_wins']/df['stake_2_wins'])
df['bet_win_2'] = amount / \
    (1+df['stake_draw']/df['stake_1_wins']+df['stake_draw']/df['stake_2_wins'])
df['bet_draw'] = amount/(1+df['stake_2_wins'] /
                         df['stake_draw']+df['stake_2_wins']/df['stake_1_wins'])


print(df[['stake_1_wins', 'stake_draw', 'stake_2_wins']])
# print(df['total_implied_prob'])
