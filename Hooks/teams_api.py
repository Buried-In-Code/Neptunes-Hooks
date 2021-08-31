import logging
from typing import Dict, Any

from requests import post
from requests.exceptions import ConnectionError, HTTPError

LOGGER = logging.getLogger(__name__)
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Neptune\'s Hooks'
}


def push_data(data: Dict[str, Any]):
    try:
        response = post(url=CONFIG['Webhooks']['Teams'], headers=HEADERS, json={
            'type': 'message',
            'attachments': [{
                'contentType': 'application/vnd.microsoft.teams.card.o365connector',
                'content': data
            }]
        })
        if response.status_code == 200:
            LOGGER.debug(f"{response.status_code}: POST - {response.url}")
        else:
            LOGGER.error(f"{response.status_code}: POST - {response.url} - {response.text}")
    except (ConnectionError, HTTPError):
        LOGGER.error(f"Unable to access: `{CONFIG['Webhooks']['Teams']}`")
