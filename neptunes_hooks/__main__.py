import logging
import time
from argparse import ArgumentParser, Namespace

from neptunes_hooks import setup_logging
from neptunes_hooks.services.microsoft_teams import MicrosoftTeams
from neptunes_hooks.services.neptunes_pride import NeptunesPride
from neptunes_hooks.settings import PlayerSettings, Settings
from neptunes_hooks.utils import parse_player_stats, parse_team_stats

LOGGER = logging.getLogger(__name__)
SETTINGS = Settings()


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-p", "--poll", nargs="?", const=30, type=int, default=30)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = get_arguments()
    setup_logging(debug=args.debug)

    LOGGER.info("Welcome to Neptune's Pride")
    neptunes_pride = NeptunesPride(
        game_number=SETTINGS.neptunes_pride.game_number,
        code=SETTINGS.neptunes_pride.api_code,
    )
    microsoft_teams = None
    if SETTINGS.webhooks.microsoft_teams:
        microsoft_teams = MicrosoftTeams(url=SETTINGS.webhooks.microsoft_teams)

    response = neptunes_pride.pull_data()
    while response and response.active:
        players = [x.username for x in response.players if x.username]
        for new_player in players:
            if new_player not in [x.username for x in SETTINGS.players]:
                SETTINGS.players.append(PlayerSettings(username=new_player))
                SETTINGS.save()

        if response.tick > SETTINGS.last_tick or args.debug:
            turn = int(response.tick / SETTINGS.neptunes_pride.tick_rate)
            LOGGER.info(f"Turn {turn:02}")

            player_stats = parse_player_stats(response, SETTINGS.players)
            team_stats = parse_team_stats(response, SETTINGS.players)

            if microsoft_teams:
                microsoft_teams.push_data(
                    player_stats=player_stats,
                    team_stats=team_stats,
                    turn=turn,
                    game_name=response.title,
                )

            SETTINGS.neptunes_pride.last_tick = response.tick
            SETTINGS.save()
            LOGGER.debug("Waiting for next turn...")
        if args.debug:
            break
        time.sleep(args.poll * 60)
        response = neptunes_pride.pull_data()


if __name__ == "__main__":
    main()
