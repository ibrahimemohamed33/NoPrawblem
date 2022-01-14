import requests

from Request_Constants import *
from API_Codes import *


def extend_url(uri_initial: str, *args: 'list[str]'):
    '''
    Extends the uri of a URL given a list of arguments
    '''
    uri = uri_initial
    for arg in args:
        if type(arg) == tuple:
            arg = arg[0]
        uri += f"/{arg.lower()}"
    return uri


def initiate_GET(endpoint: str, headers: dict, base_url=REDDIT_API_URL, params=None):
    '''
    Initiates a GET request to the Reddit API
    '''
    request_url = base_url + endpoint
    response = requests.get(url=request_url,
                            params=params,
                            headers=headers)
    if response.ok:
        return response.json()

    # If the GET request was invalid, we raise an exception
    unauthenticated_url = request_url.replace('oauth.', '')
    raise Exception(f"The request returned a {response.status_code} error for the url "
                    f"{unauthenticated_url}. The error message was '{response.reason}'")


def initiate_POST(endpoint: str, headers: dict, base_url=REDDIT_API_URL,
                  data=None, is_put=False):
    '''
    Initiates a POST requests to the endpoint, unless is_put is set to True.
    If so, it initiates a PUT request
    '''
    request_url = base_url + endpoint
    if is_put:
        response = requests.put(url=request_url,
                                data=data,
                                headers=headers)
    else:
        response = requests.post(url=request_url,
                                 data=data,
                                 headers=headers)

    request_type = 'PUT' if is_put else 'POST'
    if not response.ok:
        raise Exception(f"The {request_type} request returned a '{response.status_code}' error because: '{response.reason}'"
                        f"Make sure the inputted url '{request_url}' is intended")
