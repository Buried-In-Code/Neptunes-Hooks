# Neptune's Hooks

![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Beta-yellowgreen?style=flat-square)

[![Hatch](https://img.shields.io/badge/Packaging-Hatch-4051b5?style=flat-square)](https://github.com/pypa/hatch)
[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?style=flat-square&logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Black](https://img.shields.io/badge/Code--Style-Black-000000?style=flat-square)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/Linter-Ruff-informational?style=flat-square)](https://github.com/charliermarsh/ruff)

[![Github - Version](https://img.shields.io/github/v/tag/Buried-In-Code/Neptunes-Hooks?logo=Github&label=Version&style=flat-square)](https://github.com/Buried-In-Code/Neptunes-Hooks/tags)
[![Github - License](https://img.shields.io/github/license/Buried-In-Code/Neptunes-Hooks?logo=Github&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)
[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Neptunes-Hooks?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/Neptunes-Hooks/graphs/contributors)

A simple app that sends [Neptune's Pride](https://np.ironhelmet.com/) stats via webhooks.

## Installation

1. Make sure you have a supported version of [Python](https://www.python.org/) installed: `python --version`
2. Clone the repo: `git clone https://github.com/Buried-In-Code/Neptunes-Hooks`
3. Install the project: `pip install .`

## Execution

- `python -m neptunes_hooks`

## Arguments

*You can find all these by using the `-h` or `--help` argument*

| Argument | Flags          | Type | Default | Description                                                                              |
| -------- | -------------- | ---- | ------- | ---------------------------------------------------------------------------------------- |
| Poll     | `-p`, `--poll` | int  | 30      | Used to determine how long between polls to the Neptune's Pride API *(value in Minutes)* |
| Debug    | `--debug`      | bool | False   | Used to skip the tick check and only run once                                            |

## Socials

[![Social - Matrix](https://img.shields.io/matrix/The-Dev-Environment:matrix.org?label=The%20Dev%20Environment&logo=matrix&style=for-the-badge)](https://matrix.to/#/#The-Dev-Environment:matrix.org)
