import logging
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path

from neptunes_hooks.console import ConsoleLog
from neptunes_hooks.discord_api import push_data as push_to_discord
from neptunes_hooks.microsoft_teams_api import push_data as push_to_microsoft_teams
from neptunes_hooks.neptunes_pride_api import pull_data
from neptunes_hooks.settings import PlayerConfig, Settings
from neptunes_hooks.utils import parse_player_stats, parse_team_stats, safe_get

CONSOLE = ConsoleLog("Neptunes-Hooks")
SETTINGS = Settings()


def setup_logging(debug: bool = False):
    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler("logs/Neptunes-Hooks.log")
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] {%(name)s} | %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        level=logging.NOTSET,
        handlers=[file_handler],
    )


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-p", "--poll", nargs="?", const=30, type=int, default=30)
    parser.add_argument("-t", "--microsoft-teams", action="store_true")
    parser.add_argument("-d", "--discord", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = get_arguments()
    setup_logging(debug=args.debug)

    CONSOLE.panel("Welcome to Neptune's Pride", expand=False, style="bold blue")

    response = pull_data(game_id=SETTINGS.game_id, api_code=SETTINGS.api_code)
    while response and response["Active"]:
        players = [x["Username"] for x in response["Players"] if x["Username"]]
        for new_player in players:
            if new_player not in [x.username for x in SETTINGS.players]:
                SETTINGS.players.append(PlayerConfig(username=new_player))
                SETTINGS.save()

        if not args.microsoft_teams and not args.discord:
            break

        if response["Tick"] > SETTINGS.last_tick or args.debug:
            turn = int(response["Tick"] / SETTINGS.tick_rate)
            CONSOLE.rule(f"Turn {turn:02}", text_style="cyan", line_style="blue")

            player_stats = parse_player_stats(response, SETTINGS.players)
            team_stats = parse_team_stats(response, SETTINGS.players)

            if args.microsoft_teams:
                webhook = safe_get([x for x in SETTINGS.webhooks if x.service == "Microsoft Teams"])
                if webhook:
                    push_to_microsoft_teams(player_stats, team_stats, turn, response["Title"], webhook)
            if args.discord:
                webhook = safe_get([x for x in SETTINGS.webhooks if x.service == "Discord"])
                if webhook:
                    push_to_discord(player_stats, team_stats, turn, response["Title"], webhook)

            SETTINGS.last_tick = response["Tick"]
            SETTINGS.save()
            CONSOLE.info("Waiting for next turn...")
        if args.debug:
            break
        time.sleep(args.poll * 60)
        response = pull_data(game_id=SETTINGS.game_id, api_code=SETTINGS.api_code)


if __name__ == "__main__":
    main()
