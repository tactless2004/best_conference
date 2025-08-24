import json
import os
import cfbd
from typing import Any

def get_records(year: int) -> None:
    configuration = cfbd.Configuration(
        access_token = os.environ["API_KEY"]
    )
    api_client = cfbd.ApiClient(configuration)
    instance = cfbd.GamesApi(api_client)
    response = instance.get_records(year=year)
    return response

def get_games(year: int, team: str):
    configuration = cfbd.Configuration(
        access_token = os.environ["API_KEY"]
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
