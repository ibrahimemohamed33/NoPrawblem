import requests

from Request_Constants import *
from API_Codes import *


def authenticated_headers(script_code=SCRIPT_CODE, secret_code=SECRET_CODE) -> 'dict[str, str]':
    '''
    Runs the authentication request to secure the authorization headers to
    access the Reddit API

    Inputs:
        script_code: the private code for running the scripts that extract data
        secret_code: the extremely private code for the app that cannot be shared
    '''
    auth = requests.auth.HTTPBasicAuth(script_code, secret_code)
    OAuth_Post = requests.post(url=REDDIT_ACCESS_TOKEN_LINK,
                               auth=auth,
                               data=data,
                               headers=HEADERS)

    access_token = OAuth_Post.json()['access_token']
    return {**HEADERS, **{'Authorization': f"bearer {access_token}"}}


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


def initiate_GET(endpoint: str, base_url=REDDIT_API_URL, params=None):
    '''
    Initiates a GET request to the Reddit API
    '''
    headers = authenticated_headers()
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
