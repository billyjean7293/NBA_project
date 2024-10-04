from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
import matplotlib.pyplot as plt

# Set Pandas to display all columns
pd.set_option('display.max_columns', None)

# Define the season
SEASON = '2022-23'


# Function to get exact player ID
def get_exact_player_id(player_name):
    all_players = players.get_players()
    for player in all_players:
        if player['full_name'].lower() == player_name.lower():
            return player['id']
    print(f"No player found with name {player_name}")
    return None


# Function to plot performance over time
def plot_player_performance_over_time(player_name, game_data):
    # Ensure 'GAME_DATE' is in the correct format and sort the data
    game_data['GAME_DATE'] = pd.to_datetime(game_data['GAME_DATE'])
    game_data = game_data.sort_values(by='GAME_DATE')

    # Plot points per game over time
    plt.figure(figsize=(10, 5))
    plt.plot(game_data['GAME_DATE'], game_data['PTS'], marker='o',
             label='Points')
    plt.plot(game_data['GAME_DATE'], game_data['REB'], marker='o',
             label='Rebounds')
    plt.plot(game_data['GAME_DATE'], game_data['AST'], marker='o',
             label='Assists')

    plt.title(f"{player_name}'s Performance Over Time")
    plt.xlabel('Game Date')
    plt.ylabel('Stats')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()


# Function to gather season averages and projections
def get_player_season_averages_with_projection(player_name):
    player_id = get_exact_player_id(player_name)
    if not player_id:
        return None

    # Fetch game logs for the player
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON)
    game_data = game_log.get_data_frames()[0]

    # Ensure all required columns are in the DataFrame
    required_columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'WL']
    for col in required_columns:
        if col not in game_data.columns:
            game_data[col] = 0  # Add missing columns with zero

    # Select only necessary columns
    game_data = game_data[required_columns]

    # Ensure all columns are numeric except 'WL'
    game_data[['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']] = game_data[
        ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']].apply(pd.to_numeric,
                                                          errors='coerce')

    # Handle NaN values
    game_data.fillna(0, inplace=True)

    # Calculate overall averages
    season_averages = game_data.mean(numeric_only=True).round(1)

    # Calculate projection based on given weights
    projection = (
            season_averages.get('PTS', 0) * 1 +  # Points are worth themselves
            season_averages.get('AST', 0) * 1.5 +  # Assists are worth 1.5
            season_averages.get('REB', 0) * 1.2 +  # Rebounds are worth 1.2
            season_averages.get('STL', 0) * 5 +  # Steals are worth 5
            season_averages.get('BLK', 0) * 5 -  # Blocks are worth 5
            season_averages.get('TOV', 0) * 1  # Turnovers are worth -1
    )

    # Add the projection to the result
    season_averages['Projection'] = round(projection, 1)

    return season_averages


# Initialize a dictionary to store all stats
all_player_stats = {}

# Example player data
players_data = {
    "Best Players": [
        ("Luka Doncic", "DAL"),
        ("Giannis Antetokounmpo", "MIL"),
        ("Shai Gilgeous-Alexander", "OKC"),
        ("Jalen Brunson", "NYK"),
        ("Kevin Durant", "PHX"),
        ("Domantas Sabonis", "SAC"),
        ("Rudy Gobert", "MIN"),
        ("Anthony Davis", "LAL"),
        ("Nikola Jokic", "DEN"),
        ("Jalen Duren", "DET"),
        ("Tyrese Haliburton", "IND"),
        ("Walker Kessler", "UTA"),
        ("James Harden", "LAC"),
        ("LeBron James", "LAL"),
        ("Devin Booker", "PHX"),
        ("Joel Embiid", "PHI")
    ],
}

# Loop through each category and player
for category, player_list in players_data.items():
    for player_name, team in player_list:
        print(f"Fetching stats for {player_name} ({team})...")

        # Fetch game logs for the player
        player_id = get_exact_player_id(player_name)
        if not player_id:
            continue  # Skip player if not found

        game_log = playergamelog.PlayerGameLog(player_id=player_id,
                                               season=SEASON)
        game_data = game_log.get_data_frames()[0]

        # Ensure all required columns are in the DataFrame
        required_columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'WL',
                            'GAME_DATE']
        for col in required_columns:
            if col not in game_data.columns:
                game_data[col] = 0  # Add missing columns with zero

        # Select only necessary columns
        game_data = game_data[required_columns]

        # Ensure all columns are numeric except 'WL' and 'GAME_DATE'
        game_data[['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']] = game_data[
            ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']].apply(pd.to_numeric,
                                                              errors='coerce')

        # Handle NaN values
        game_data.fillna(0, inplace=True)

        # Plot the player's performance over time
        plot_player_performance_over_time(player_name, game_data)

        # Store season averages and projections
        stats = get_player_season_averages_with_projection(player_name)
        if stats is not None:
            all_player_stats[player_name] = stats

# Convert all stats to a DataFrame
stats_df = pd.DataFrame(all_player_stats).T
stats_df.columns = ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks',
                    'Turnovers', 'Projection']

# Sort the DataFrame by the Projection column in descending order
stats_df = stats_df.sort_values(by='Projection', ascending=False)

# Print the sorted DataFrame
print(stats_df)
