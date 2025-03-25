import re
from typing import Optional

import requests


def parse_to_header(headers: str) -> Optional[str]:
    match = re.search('\\["To",([^\\]]*)\\]', headers)
    if not match:
        return None
    return match.group(1)


def parse_conversation_id_from_headers(headers: str) -> Optional[int]:
    to = parse_to_header(headers)
    if not to:
        return None
    match = re.search('\\.(\\d+)[^\\s]*\\s<', to)
    if not match:
        return None
    return int(match.group(1))


def send_mail(url: str, **kwargs):
    if not url:
        raise Exception('url is unspecified')

    api_key = kwargs.get('api_key')
    if not api_key:
        raise Exception('api_key is unspecified')

    data = kwargs.get('data')
    if not data:
        raise Exception('data is unspecified')

    response = requests.post(url, auth=("api", api_key), data=data)
    # throw an error if we got a failure from the Mailgun API
    response.raise_for_status()
    return response
