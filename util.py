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