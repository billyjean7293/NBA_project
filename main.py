from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

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

# Function to gather stats for a player
def get_player_season_averages_with_projection(player_name):
    # Use the updated function to get player ID
    player_id = get_exact_player_id(player_name)
    if not player_id:
        return None

    # Fetch game logs for the player
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON)
    game_data = game_log.get_data_frames()[0]

    # Ensure all required columns are in the DataFrame
    required_columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']
    for col in required_columns:
        if col not in game_data.columns:
            game_data[col] = 0  # Add missing columns with zero

    # Select only necessary columns
    game_data = game_data[required_columns]

    # Ensure all columns are numeric
    game_data = game_data.apply(pd.to_numeric, errors='coerce')

    # Handle NaN values
    game_data.fillna(0, inplace=True)

    # Calculate the season averages and round to 1 decimal place
    season_averages = game_data.mean(numeric_only=True).round(1)

    # Calculate projection based on given weights
    projection = (
        season_averages.get('PTS', 0) * 1 +  # Points are worth themselves
        season_averages.get('AST', 0) * 1.5 +  # Assists are worth 1.5
        season_averages.get('REB', 0) * 1.2 +  # Rebounds are worth 1.2
        season_averages.get('STL', 0) * 5 +  # Steals are worth 5
        season_averages.get('BLK', 0) * 5 -  # Blocks are worth 5
        season_averages.get('TOV', 0) * 1   # Turnovers are worth -1
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
        ("Joel Embiid", "PHI"),
        ("Kyrie Irving", "DAL")
    ],
}

# Loop through each category and player
for category, player_list in players_data.items():
    for player_name, team in player_list:
        print(f"Fetching stats for {player_name} ({team})...")
        stats = get_player_season_averages_with_projection(player_name)
        if stats is not None:
            # Store the stats in the dictionary
            all_player_stats[player_name] = stats

# Convert all stats to a DataFrame
stats_df = pd.DataFrame(all_player_stats).T
stats_df.columns = ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers', 'Projection']

# Sort the DataFrame by the Projection column in descending order
stats_df = stats_df.sort_values(by='Projection', ascending=False)

# Print the sorted DataFrame
print(stats_df)
