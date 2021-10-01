import logging
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path

import painted_logger

from neptunes_hooks import (
    is_teamed,
    load_config,
    parse_player_stats,
    parse_team_stats,
    post_to_discord,
    post_to_teams,
    request_data,
    save_config,
)

LOGGER = logging.getLogger("Neptunes-Hooks")

TIMEOUT = 100


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-p", "--poll", nargs="?", const=30, type=int, default=30)
    parser.add_argument("-t", "--teams", action="store_true")
    parser.add_argument("-d", "--discord", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = get_arguments()
    painted_logger.init(
        root_path=Path(__file__).resolve().parent.parent,
        file_level=logging.DEBUG if args.debug else logging.INFO,
        console_level=logging.INFO if args.debug else logging.WARNING,
    )

    config = load_config()
    np_response = request_data(
        game_id=config["Neptune's Pride"]["Game ID"], api_code=config["Neptune's Pride"]["API Code"]
    )
    LOGGER.debug(f"Neptune's Response: {np_response}")
    while np_response and np_response["Active"]:
        new_players = []
        np_players = [player["Username"] for player in np_response["Players"] if player["Username"]]
        for new_player in np_players:
            if new_player not in config["Players"].keys():
                config["Players"][new_player] = {"Team": None}
                save_config(config)
                new_players.append(new_player)
        if np_response["Tick"] > config["Neptune's Pride"]["Last Tick"] or args.debug:
            player_stats = parse_player_stats(np_response, config)
            LOGGER.debug(player_stats)

            team_stats = parse_team_stats(np_response, config) if is_teamed(config) else None
            LOGGER.debug(team_stats)

            turn = int(np_response["Tick"] / config["Neptune's Pride"]["Tick Rate"])

            if args.teams:
                post_to_teams(player_stats, team_stats, turn, np_response["Title"], config)
            if args.discord:
                post_to_discord(player_stats, team_stats, turn, np_response["Title"], config)
            config["Neptune's Pride"]["Last Tick"] = np_response["Tick"]
            save_config(config)
            LOGGER.info("Waiting for next turn...")
        if args.debug:
            break
        time.sleep(args.poll * 60)
        np_response = request_data(
            game_id=config["Neptune's Pride"]["Game ID"], api_code=config["Neptune's Pride"]["API Code"]
        )
        LOGGER.debug(f"Neptune's Response: {np_response}")


if __name__ == "__main__":
    main()
