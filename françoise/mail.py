import requests

def send_mail(url: str, **kwargs):
    if not url:
        raise Exception('url is unspecified')

    api_key = kwargs.get('api_key')
    if not api_key:
        raise Exception('api_key is unspecified')

    data = kwargs.get('data')
    if not data:
        raise Exception('data is unspecified')

    return requests.post(url, auth=("api", api_key), data=data)
