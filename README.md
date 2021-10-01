# Neptune's Hooks

![Python](https://img.shields.io/badge/Python-3.7%20|%203.8%20|%203.9-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Alpha-yellow?style=for-the-badge)
[![Code Style - Black](https://img.shields.io/badge/Code--Style-Black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

[![Github - Version](https://img.shields.io/github/v/tag/Buried-In-Code/Neptunes-Hooks.svg?logo=Github&label=Version&style=for-the-badge)](https://github.com/Buried-In-Code/Neptunes-Hooks/tags)
[![Github - License](https://img.shields.io/github/license/Buried-In-Code/Neptunes-Hooks.svg?logo=Github&label=License&style=for-the-badge)](https://opensource.org/licenses/GPL-3.0)
[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Neptunes-Hooks.svg?logo=Github&label=Contributors&style=for-the-badge)](https://github.com/Buried-In-Code/Neptunes-Hooks/graphs/contributors)

[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Neptunes-Hooks/Code-Analysis?logo=Github-Actions&label=Code-Analysis&style=for-the-badge)](https://github.com/Buried-In-Code/Neptunes-Hooks/actions/workflows/code-analysis.yaml)

A simple app that sends Neptune's Pride Stats to webhooks.  
Currently, supports:
- Microsoft Teams

## Arguments

| Argument  | Type | Required | Default | Notes |
| --------- | ---- | -------- | ------- | ----- |
| `--debug` | bool | False    | False   |       |

## Execution

~~All settings can be found in `~/.config/Neptunes-Hooks/settings.ini`  
*Requires restart for changes to take effect*~~

### From Source

1. Make sure you have [Poetry](https://python-poetry.org) installed
2. Clone the repo: `git clone https://github.com/Buried-In-Code/Neptunes-Hooks`
3. Navigate to the folder: `cd Neptunes-Hooks/`
4. Run: `poetry install`
5. Run `poetry run Neptunes-Hooks` *Generates default files*
6. Update the generated `config.yaml` with your:
    - Game Number
    - API Code
    - Tick Rate
    - Player Usernames and/or Teams
    - MS Teams Webhook
    - Discord Webhook
7. Run `poetry run Neptunes-Hooks`

## Arguments

*You can find all these by using the `-h` or `--help` argument*

| Argument         | Type  | Default | Choices        | Example                         | Description                                                                                |
| ---------------- | ----- | ------- | -------------- | ------------------------------- | ------------------------------------------------------------------------------------------ |
| Poll             | int   | 30      |                | `python -m Teams 30`            | Used to determine how long between polls to the Neptune's Pride API *(value in Minutes)*   |
| Hooks *Required* | [str] |         | teams, discord | `python -m Teams --hooks teams` | Select which platform to send the updates to *(Requires a valid URL in the `config.yaml`)* |
| Testing          | bool  | False   |                | `python -m Teams --testing`     | Used to skip the tick check and use test config                                            |

## Socials

[![Social - Discord](https://img.shields.io/discord/618581423070117932.svg?logo=Discord&label=The-DEV-Environment&style=for-the-badge&colorB=7289da)](https://discord.gg/nqGMeGg)

![Social - Email](https://img.shields.io/badge/Email-BuriedInCode@tuta.io-red?style=for-the-badge&logo=Tutanota&logoColor=red)

[![Social - Twitter](https://img.shields.io/badge/Twitter-@BuriedInCode-blue?style=for-the-badge&logo=Twitter)](https://twitter.com/BuriedInCode) 