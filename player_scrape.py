import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse, parse_qs, urljoin

BASE_URL = 'http://hunfloorball.hu/'

def scrape_player_scores():
    url = 'http://hunfloorball.hu/index.php?pg=floorball_players&year=0910'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the seasons (years)
    select_season = soup.find('select', {'id': 'year'})
    seasons = [option['value'] for option in select_season.find_all('option')]

    player_scores_data = []

    for season in seasons:
        season_url = f'http://hunfloorball.hu/index.php?pg=floorball_players&year={season}'
        season_response = requests.get(season_url)
        season_soup = BeautifulSoup(season_response.text, 'html.parser')

        # Find the player scores table within the div with id "players"
        players_div = season_soup.find('div', {'id': 'players'})
        player_scores_tbody = players_div.find('tbody')

        print(f"Season: {season}")  # Print the season

        for row in player_scores_tbody.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 1:
                player_name = columns[1].get_text(strip=True)
                player_team = columns[2].get_text(strip=True)
                player_score = columns[3].get_text(strip=True)
                player_matches = columns[4].get_text(strip=True)

                player_data = {
                    'season': season,
                    'name': player_name,
                    'team': player_team,
                    'score': player_score,
                    'matches': player_matches
                }
                player_scores_data.append(player_data)

                # Print the player data
                print(f"{player_name} ({player_team}): {player_score} points in {player_matches} matches")

        print("\n")  # Add an empty line between seasons

    with open('player_scores.json', 'w', encoding='utf-8') as f:
        json.dump(player_scores_data, f, ensure_ascii=False, indent=4)

# Call the scrape_player_scores function to scrape the player scores data
scrape_player_scores()
