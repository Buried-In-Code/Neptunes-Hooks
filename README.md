# Neptune's Hooks
[![Version](https://img.shields.io/github/tag-pre/Macro303/Neptunes-Hooks.svg?label=version&style=flat-square)](https://github.com/Macro303/Neptunes-Hooks/releases)
[![Issues](https://img.shields.io/github/issues/Macro303/Neptunes-Hooks.svg?style=flat-square)](https://github.com/Macro303/Neptunes-Hooks/issues)
[![Contributors](https://img.shields.io/github/contributors/Macro303/Neptunes-Hooks.svg?style=flat-square)](https://github.com/Macro303/Neptunes-Hooks/graphs/contributors)
[![License](https://img.shields.io/github/license/Macro303/Neptunes-Hooks.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A simple app that sends Neptune's Pride Stats to webhooks.  
Currently, supports:
- Microsoft Teams

## Built Using

- [Python: 3.9.2](https://www.python.org/)
- [pip: 21.0.1](https://pypi.org/project/pip/)
- [requests: 2.25.1](https://pypi.org/project/requests/)
- [ruamel.yaml: 0.17.9](https://pypi.org/project/ruamel.yaml/)

## Execution

1. Execute the following to generate the default files:
   ```bash
   $ pip install -r requirements.txt
   $ python -m Hooks
   ```
2. Update the generated `config.yaml` with your:
    - Game Number
    - API Code
    - Tick Rate
    - Player Usernames and/or Teams
    - MS Teams Webhook
    - Discord Webhook
3. Run the following:
   ```bash
   $ python -m Hooks
   ```

## Arguments

*You can find all these by using the `-h` or `--help` argument*

| Argument | Type | Default | Choices | Example | Description |
| -------- | ---- | ------- | ------- | ------- | ----------- |
| Poll | int | 30 | | `python -m Teams 30` | Used to determine how long between polls to the Neptune's Pride API *(value in Minutes)* |
| Hooks *Required* | [str] | | teams, discord | `python -m Teams --hooks teams` | Select which platform to send the updates to *(Requires a valid URL in the `config.yaml`)* |
| Testing | bool | False | | `python -m Teams --testing` | Used to skip the tick check and use test config |

## Socials
[![Discord | The DEV Environment](https://invidget.switchblade.xyz/618581423070117932)](https://discord.gg/nqGMeGg)