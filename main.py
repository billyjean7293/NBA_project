from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Define the season
SEASON = '2022-23'

# Function to gather stats for a player
def get_player_season_averages_with_projection(player_name):
    # Find player ID
    player_info = players.find_players_by_full_name(player_name)

    if not player_info:
        print(f"No player found with name {player_name}")
        return None

    player_id = player_info[0]['id']

    # Fetch game logs for the player
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON)
    game_data = game_log.get_data_frames()[0]

    # Select only necessary columns
    game_data = game_data[['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']]

    # Calculate the season averages and round to 1 decimal place
    season_averages = game_data.mean().round(1)

    # Calculate projection based on given weights
    projection = (
            season_averages['PTS'] * 1 +  # Points are worth themselves
            season_averages['AST'] * 1.5 +  # Assists are worth 1.5
            season_averages['REB'] * 1.2 +  # Rebounds are worth 1.2
            season_averages['STL'] * 5 +  # Steals are worth 5
            season_averages['BLK'] * 5 -  # Blocks are worth 5
            season_averages['TOV'] * 1   #turnovers are worth -1
    )

    # Add the projection to the result
    season_averages['Projection'] = round(projection, 1)

    return season_averages


# Test the function for LeBron James
lebron_averages_with_projection = (
    get_player_season_averages_with_projection('Luka Doncic'))
print(lebron_averages_with_projection)



