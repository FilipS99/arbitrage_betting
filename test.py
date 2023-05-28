import pandas as pd


df = pd.read_excel(
    'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\20230528_103600.xlsx')

# df = rename_synonyms(df)

# DataFrame with stake_1_wins and URLs
df_stake_1_wins = df[['team_1','team_2','stake_1_wins','url']]
# pd.DataFrame({
#     'team_1': ['Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie', 'Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie'],
#     'team_2': ['Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia', 'Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia'],
#     'stake_1_wins': [2.90, 1.35, 1.90, 3.50, 3.10, 1.67, 3.00, 1.00, 2.00, 3.00, 3.00, 2.00],
#     'url': ['https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'link2', 'link2', 'link2', 'link2', 'link2', 'link2']
# })

# DataFrame with stake_draw and URLs
df_stake_draw = df[['team_1','team_2','stake_draw','url']]
# pd.DataFrame({
#     'team_1': ['Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie', 'Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie'],
#     'team_2': ['Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia', 'Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia'],
#     'stake_draw': [3.40, 5.25, 3.60, 3.75, 3.40, 4.00, 3.40, 5.00, 3.00, 3.00, 4.00, 4.00],
#     'url': ['https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'link2', 'link2', 'link2', 'link2', 'link2', 'link2']
# })

# DataFrame with stake_2_wins and URLs
df_stake_2_wins = df[['team_1','team_2','stake_2_wins','url']]
# pd.DataFrame({
#     'team_1': ['Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie', 'Głogów', 'W.Kraków', 'Opole', 'GKSTychy', 'SkraCz.', 'Podbeskidzie'],
#     'team_2': ['Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia', 'Łęczna', 'Sosnowiec', 'Chojniczanka', 'StalRzeszów', 'Niepołomice', 'Resovia'],
#     'stake_2_wins': [2.45, 8.50, 4.20, 2.00, 2.30, 5.00, 2.45, 8.00, 4.00, 2.00, 3.00, 6.00],
#     'url': ['https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...', 'https://superbet.pl/zaklady-bukmacherskie/pilk...',
#             'link2', 'link2', 'link2', 'link2', 'link2', 'link2']
# })

# Merge the dataframes on team names
df_merged = pd.merge(df_stake_1_wins, df_stake_draw, on=['team_1', 'team_2'])
df_merged = pd.merge(df_merged, df_stake_2_wins, on=['team_1', 'team_2'])

# Create a new dataframe with matching URLs, stake values for wins, draw, and 2 wins
df_new = pd.DataFrame({
    'team_1': df_merged['team_1'],
    'team_2': df_merged['team_2'],
    'url_1_wins': df_merged['url_x'],
    'stake_1_wins': df_merged['stake_1_wins'],
    'url_draw': df_merged['url_y'],
    'stake_draw': df_merged['stake_draw'],
    'url_2_wins': df_merged['url'],
    'stake_2_wins': df_merged['stake_2_wins']
})

# print(df_new)

# Calculate the sum of implied probabilities
df_new['total_implied_prob'] = 1 / df_new['stake_1_wins'] + \
    1 / df_new['stake_draw'] + 1 / df_new['stake_2_wins']

# Total amount to bet
amount = 1000

# Calculate tbet amounts
df_new['bet_win_1'] = amount / \
    (1+df_new['stake_1_wins']/df_new['stake_draw'] +
     df_new['stake_1_wins']/df_new['stake_2_wins'])
df_new['bet_win_2'] = amount / \
    (1+df_new['stake_draw']/df_new['stake_1_wins']+df_new['stake_draw']/df_new['stake_2_wins'])
df_new['bet_draw'] = amount/(1+df_new['stake_2_wins'] /
                         df_new['stake_draw']+df_new['stake_2_wins']/df_new['stake_1_wins'])


df_new['profit'] = df_new['bet_win_1'] * df_new['stake_1_wins'] - amount

df_new = df_new.sort_values('profit')

# print(df_new[['stake_1_wins', 'stake_draw', 'stake_2_wins']/])
# print(df_new['total_implied_prob'])

# save CSV file
filename = "test7.xlsx"
output_path = 'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\'
df_new.to_excel(output_path+filename,
            header=True, index=False)