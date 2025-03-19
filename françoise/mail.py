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

    response = requests.post(url, auth=("api", api_key), data=data)
    # throw an error if we got a failure from the Mailgun API
    response.raise_for_status()
    return response
