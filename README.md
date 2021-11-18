# Neptune's Hooks

![Python](https://img.shields.io/badge/Python-3.7%20|%203.8%20|%203.9%20|%203.10-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Beta-yellowgreen?style=flat-square)

[![Black](https://img.shields.io/badge/Black-Enabled-000000?style=flat-square)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/Flake8-Enabled-informational?style=flat-square)](https://github.com/PyCQA/flake8)
[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)

[![Github - Version](https://img.shields.io/github/v/tag/Buried-In-Code/Neptunes-Hooks?logo=Github&label=Version&style=flat-square)](https://github.com/Buried-In-Code/Neptunes-Hooks/tags)
[![Github - License](https://img.shields.io/github/license/Buried-In-Code/Neptunes-Hooks?logo=Github&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)
[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Neptunes-Hooks?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/Neptunes-Hooks/graphs/contributors)

[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Neptunes-Hooks/Code-Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/Neptunes-Hooks/actions/workflows/code-analysis.yaml)

A simple app that sends [Neptune's Pride](https://np.ironhelmet.com/) stats via webhooks.

## Execution

All settings can be found in `~/.config/Neptunes-Hooks/settings.ini`  
*Requires restart for changes to take effect.*

### From Source
1. Make sure you have [Poetry](https://python-poetry.org) installed
2. Clone the repo: `git clone https://github.com/Buried-In-Code/Neptunes-Hooks`
3. Navigate to the folder: `cd Neptunes-Hooks/`
4. Run: `poetry install`
5. Run `poetry run Neptunes-Hooks`
6. Update `settings.ini` with the Game config
7. Run `poetry run Neptunes-Hooks`

## Arguments

*You can find all these by using the `-h` or `--help` argument*

| Argument | Flags | Type | Default | Description |
| -------- | ----- | ---- | ------- | ----------- |
| Poll | `-p`, `--poll` | int | 30 | Used to determine how long between polls to the Neptune's Pride API *(value in Minutes)* |
| Microsoft Teams | `-t`, `--microsoft-teams` | bool | False | Run using Microsoft Teams hook |
| Discord | `-d`, `--discord` | bool | False | Run using Discord hook |
| Debug | `--debug` | bool | False | Used to skip the tick check and only run once |

## Socials

[![Social - Discord](https://img.shields.io/badge/Discord-The--DEV--Environment-7289DA?logo=Discord&style=flat-square)](https://discord.gg/nqGMeGg)
[![Social - Matrix](https://img.shields.io/badge/Matrix-The--DEV--Environment-informational?logo=Matrix&style=flat-square)](https://matrix.to/#/#the-dev-environment:matrix.org)

[![Social - Twitter](https://img.shields.io/badge/Twitter-@BuriedInCode-informational?logo=Twitter&style=flat-square)](https://twitter.com/BuriedInCode)
[![Social - Mastodon](https://img.shields.io/badge/Mastodon-@BuriedInCode@fosstodon.org-informational?logo=Mastodon&style=flat-square)](https://fosstodon.org/@BuriedInCode)
