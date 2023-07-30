import pandas as pd


def calculate_bets_outcomes(df: pd.DataFrame, amount: float, output_path: str, filename: str):
    df_copy = df.copy()

    # taxes ;//
    taxed_amount = amount*0.88

    df_copy['stake_1_wins'] = df_copy['stake_1_wins'].astype(float)
    df_copy['stake_draw'] = df_copy['stake_draw'].astype(float)
    df_copy['stake_2_wins'] = df_copy['stake_2_wins'].astype(float)

    # DataFrame with stake_1_wins and URLs
    df_stake_1_wins = df_copy[['game_datetime', 'team_1', 'team_2', 'stake_1_wins', 'url', 'category']]

    # DataFrame with stake_draw and URLs
    df_stake_draw = df_copy[['game_datetime', 'team_1', 'team_2', 'stake_draw', 'url', 'category']]

    # DataFrame with stake_2_wins and URLs
    df_stake_2_wins = df_copy[['game_datetime', 'team_1', 'team_2', 'stake_2_wins', 'url', 'category']]

    # Merge the dataframes on team names
    df_merged = pd.merge(df_stake_1_wins, df_stake_draw,
                         on=['game_datetime', 'team_1', 'team_2', 'category'])
    df_merged = pd.merge(df_merged, df_stake_2_wins, on=['game_datetime', 'team_1', 'team_2', 'category'])
                  
    # Create a new dataframe with matching URLs, stake values for wins, draw, and 2 wins
    df_new = pd.DataFrame({
        'game_datetime': df_merged['game_datetime'],
        'team_1': df_merged['team_1'],
        'team_2': df_merged['team_2'],
        'category': df_merged['category'],
        'url_1_wins': df_merged['url_x'],
        'stake_1_wins': df_merged['stake_1_wins'],
        'url_draw': df_merged['url_y'],
        'stake_draw': df_merged['stake_draw'],
        'url_2_wins': df_merged['url'],
        'stake_2_wins': df_merged['stake_2_wins']
    })

    # Calculate the sum of implied probabilities
    df_new['total_implied_prob'] = 1. / df_new['stake_1_wins'] + \
        1. / df_new['stake_draw'] + 1. / df_new['stake_2_wins']

    # Calculate bet taxed_amounts
    df_new['bet_win_1_taxed_amount'] = taxed_amount / \
        (1+df_new['stake_1_wins']/df_new['stake_draw'] +
         df_new['stake_1_wins']/df_new['stake_2_wins'])
    df_new['bet_win_2_taxed_amount'] = taxed_amount / \
        (1+df_new['stake_2_wins']/df_new['stake_1_wins'] +
         df_new['stake_2_wins']/df_new['stake_draw'])
    df_new['bet_draw_taxed_amount'] = taxed_amount/(1+df_new['stake_draw'] /
                                       df_new['stake_1_wins']+df_new['stake_draw']/df_new['stake_2_wins'])

    # Calculate bet pre taxed amounts
    df_new['bet_win_1_untaxed_amount'] = amount / \
        (1+df_new['stake_1_wins']/df_new['stake_draw'] +
         df_new['stake_1_wins']/df_new['stake_2_wins'])
    df_new['bet_win_2_untaxed_amount'] = amount / \
        (1+df_new['stake_2_wins']/df_new['stake_1_wins'] +
         df_new['stake_2_wins']/df_new['stake_draw'])
    df_new['bet_draw_untaxed_amount'] = amount/(1+df_new['stake_draw'] /
                                       df_new['stake_1_wins']+df_new['stake_draw']/df_new['stake_2_wins'])

    df_new['profit'] = df_new['bet_win_1_taxed_amount'] * df_new['stake_1_wins'] - amount

    df_new = df_new.sort_values('profit', ascending=False)

    # display info
    # file tends to exceed max size
    df_new = df_new[df_new['profit'] > -0.15*amount]

    # Count the rows where 'column_name' is positive
    positive_count = len(df_new[df_new['profit'] > 0])

    # Print the positive profit count
    print("\nNumber of rows where profit is positive:", positive_count)

    # Round 'Column1' to two decimal places
    columns_to_round = ['total_implied_prob', 'bet_win_1_taxed_amount', 'bet_win_2_taxed_amount', 'bet_draw_taxed_amount', 'bet_win_1_untaxed_amount', 'bet_win_2_untaxed_amount', 'bet_draw_untaxed_amount', 'profit']

    df_new[columns_to_round] = df_new[columns_to_round].round(2)

    df_new = df_new.drop_duplicates()
    
    # save CSV file
    df_new.to_excel(output_path+filename+"_bets.xlsx",
                    header=True, index=False)


# # testing

# df = pd.read_excel(
#     'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\20230528_103600.xlsx')
