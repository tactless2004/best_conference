import json
import os
from typing import Any
import cfbd

# Global constantst
conference_name_map_file = {
    "Big Ten" : "Big_Ten",
    "Big 12" : "Big_12",
    "ACC" : "ACC",
    "SEC" : "SEC"
}

def get_records(year: int) -> None:
    configuration = cfbd.Configuration(
        access_token = os.getenv("API_KEY")
    )
    api_client = cfbd.ApiClient(configuration)
    instance = cfbd.GamesApi(api_client)
    response = instance.get_records(year=year)
    return response

def get_games(year: int, team: str):
    configuration = cfbd.Configuration(
        access_token = os.getenv("API_KEY")
    )
    api_client = cfbd.ApiClient(configuration)
    instance = cfbd.GamesApi(api_client)
    response = instance.get_games(year=year, team=team)
    return response

def get_conference_teams(conference: str):
    with open("2024_records.txt", "r", encoding = "utf-8") as f:
        # Greatest line of all time
        return [x.partition('team=\'')[2].split('\'')[0] for x in f.readlines() if f'conference=\'{conference}\'' in x]

def write_response(filename: str, response: Any) -> None:
    with open(filename, "w+", encoding = "utf-8") as f:
        for line in response:
            f.write(f"{str(line)}\n")

EXPONENTIAL_SMOOTHING = 0.5
def preprocess_conference(teams_in_conference) -> list:
    n = len(teams_in_conference)
    teams_in_conference = sorted(
        teams_in_conference,
        key = lambda team: _compute_win_loss_ratio(team),
        reverse = True
    )

    return [
        (name, 1/(i+1)**EXPONENTIAL_SMOOTHING) for i,name in enumerate(teams_in_conference)
    ]

def _compute_win_loss_ratio(teamname: str) -> float:
    # This is truthfully some of the ugliest code I've ever written, but it works.
    team_data = open("2024_records.txt", "r", encoding = "utf-8").readlines()
    idx = -1
    for i, row in enumerate(team_data):
        if row.partition('team=\'')[2].split('\'')[0] == teamname:
            idx = i

    if idx == -1:
        raise ValueError(f"{teamname} was not found")
    conference_games_data = team_data[idx].partition('conference_games=TeamRecord(')[2].split(')')[0]
    return float(int(conference_games_data.partition('wins=')[2].split(",")[0])/int(conference_games_data.partition('games=')[2].split(",")[0]))

def generate_conference_rank_json(conferences: list, write = False, write_path = "conference_team_ranks.json") -> dict:
    assert conferences != []
    # Generates a dictionary of the structure:
    # {
    #   "SEC" : ["Alabama", "Missouri", ...],
    #   "Big 12" : ["Iowa State", "Kansas", ...],
    #   ...
    # }
    conference_team_map = {
        conference : get_conference_teams(conference) for conference in conferences
    }
    # Generates a dictionary of the structure:
    # {
    #       "SEC" : {
    #           "Alabama" : 1.0,
    #           "Georgia" : 0.87,
    #           ...
    #       },
    #       "Big Ten" : {
    #           "Ohio State" : 1.0,
    #           "Michigan" : 0.89,
    #           ...
    #       },
    #       ...
    # }
    conference_team_score_map = {}
    for conference in conferences:
        preprocessed_conference = preprocess_conference(conference_team_map[conference])
        conference_team_score_map[conference] = {
            processed_team[0] : processed_team[1] for processed_team in preprocessed_conference
        }
    if write:
        with open(write_path, "w+", encoding = "utf-8") as f:
            json.dump(
                obj = conference_team_score_map,
                fp = f,
                indent = 4
            )

    return conference_team_score_map

def compute_points_for_winner(loser_rank: float, winner_rank: float) -> float:
    return loser_rank/winner_rank

def write_games_data(team, conference) -> None:
    '''write_response() and get_games() simplified and makes consistent names.'''
    write_response(f"game_stats/{conference_name_map_file[conference]}_{team}_gamedata.txt", get_games(2024, team))

def write_all_games_data(conferences: list):
    with open("conference_team_ranks.json", "r", encoding = "utf-8") as f:
        conference_rank_data = json.load(f)

    for conference in conferences:
        assert isinstance(conference_rank_data[conference], dict)
        for team in conference_rank_data[conference].keys():
            write_games_data(team, conference)
def score_game(team: str, game_data: str, opponent_conferences: list) -> float:
    '''Score individual game for an individual'''
    # DRY (Don't repeat yourself)
    def grab_field(text: str, start_str):
        '''
        Grab all the text after the start string then look for the first element enclosed in single quotes
        '''
        text = text.partition(start_str)[2]
        start = text.find("'")
        end = text.find("'", start + 1)
        return text[start + 1:end]

    def grab_points(text: str):
        home_points = int(text.partition("home_points=")[2].split(" ")[0])
        away_points = int(text.partition("away_points=")[2].split(" ")[0])
        return home_points, away_points

    # Rank data for use in scoring (if needed)
    with open("conference_team_ranks.json", "r", encoding = "utf-8") as f:
        rank_data = json.load(f)

    # Parse the game_data for all relevant fields
    home_team = grab_field(game_data, "home_team=")
    away_team = grab_field(game_data, "away_team=")
    home_conference = grab_field(game_data, "home_conference=")
    away_conference = grab_field(game_data, "away_conference=")
    home_points, away_points = grab_points(game_data)

    if team == home_team:
        # If the opponent team is not an opposing P4 Conference, we will not consider this game.
        if away_conference not in opponent_conferences:
            return 0.0

        # If team won
        if home_points > away_points:
            return compute_points_for_winner(
                loser_rank = float(rank_data[away_conference][away_team]),
                winner_rank = float(rank_data[home_conference][home_team])
            )

    elif team == away_team:
        # If the opponent team is not an opposing P4 Conference, we will not consider this game.
        if home_conference not in opponent_conferences:
            return 0.0

        # If team won
        if away_points > home_points:
            return compute_points_for_winner(
                winner_rank = float(rank_data[away_conference][away_team]),
                loser_rank = float(rank_data[home_conference][home_team])
            )
    else:
        raise RuntimeError(f"provided team, {team} was not found in team data")
    return 0.0
def process_games(team, team_conference) -> float:
    '''
    Iterate overall games played by a team and,
    compute the points earned for interconference play (if any).
    '''
    total_score = 0.0

    opponent_conferences = list(
        set(
            ["ACC", "SEC", "Big 12", "Big Ten"]).difference(
                set([team_conference])
        )
    )

    with open(
        file = f"game_stats/{conference_name_map_file[team_conference]}_{team}_gamedata.txt",
        mode = "r",
        encoding = "utf-8"
    ) as f:
        games_data = f.readlines()

    for game_data in games_data:
        total_score += score_game(team, game_data, opponent_conferences)

    return total_score

def process_all_teams(conferences: list) -> dict:
    '''
    Process all teams games for each conference and determine conference ranks
    '''
    conference_ranks = {}
    conference_rank_data = generate_conference_rank_json(conferences)
    for conference in conferences:
        conf_score = 0.0
        assert isinstance(conference_rank_data[conference], dict)
        for team in conference_rank_data[conference].keys():
            conf_score += process_games(team, conference)
        conference_ranks[conference] = conf_score

    return conference_ranks
