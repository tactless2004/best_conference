import cfbd
import os
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
