import requests
import pandas as pd

from API_Codes import *
from Request_Constants import *

DATAFRAME_COLUMNS = ['Post_ID', 'Post_Title', 'Post_Subtext',
                     'Num_Comments_On_Post', 'Comments']

INDEX = DATAFRAME_COLUMNS[0]


def authenticated_headers(script_code: str, secret_code: str) -> 'dict[str, str]':
    '''
    Runs the authentication request to secure access for Reddit's API

    Inputs:
        script_code: the private code for running the scripts that extract data
        secret_code: the extremely private code for the app that cannot be shared
    '''
    auth = requests.auth.HTTPBasicAuth(script_code, secret_code)
    OAuth_Post = requests.post(REDDIT_ACCESS_TOKEN_LINK, auth=auth, data=data,
                               headers=HEADERS)

    access_token = OAuth_Post.json()['access_token']
    return {**HEADERS, **{'Authorization': f"bearer {access_token}"}}


def configure_url(sub_name: str, is_username: bool) -> str:
    '''
    Takes the name of a desired subreddit or user and then converts it into the proper
    url within the OAuth system

    Inputs:
        sub_name: the name of the subreddit
        is_username: whether the subreddit is a username or subreddit page
    '''
    redirected_character = 'user' if is_username else 'r'
    return extend_url(REDDIT_URL, redirected_character, sub_name)


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


class SubRedditRequest:
    def __init__(self, is_username: bool, name: str) -> None:
        '''
        Initializes the Reddit Request class

        Inputs:
            name: the name of the subreddit or username to extract the post
            is_username: whether the name is a username or a subreddit page
        '''
        self.headers = authenticated_headers(PERSONAL_USE_SCRIPT, SECRET_CODE)
        self.url = configure_url(name, is_username)
        self.dataframe = pd.DataFrame(columns=DATAFRAME_COLUMNS, index=[INDEX])

    def __repr__(self) -> str:
        return f"Now requesting data from the url '{self.url.replace('oauth.', '')}'"

    def __initiate_GET(self, params: dict or None, *args):
        '''
        Creates a get request to the Reddit API and returns the content if the
        request was successful. Otherwise, it raises an exception
        '''
        request_url = extend_url(self.url, args)
        response = requests.get(request_url, params, headers=self.headers)
        if response.ok:
            return response.json()

        # If the get request was invalid, we raise an exception
        unauthenticated_url = request_url.replace('oauth.', '')
        raise Exception(
            f"The request returned a {response.status_code} error for the url "
            f"{unauthenticated_url}. The error message was '{response.reason}'"
        )

    def get_reddit_posts(self, listing: str, t: str or None, limit: int) -> 'list[dict]':
        '''
        Makes a GET request to the server to receive the first N reddit posts
        under a listing, where N is the limit and t is the time query if the
        listing searches for the top posts: (hour, day, week, month, year, all)
        '''
        params = {'limit': limit}
        if t and listing == 'top':
            params['t'] = t.lower()

        data = self.__initiate_GET(params, listing)
        return data['data']['children']

    def fetch_comments(self, child_id: str) -> 'list[str]':
        '''
        Extracts all the comments under a reddit post and returns a list
        '''
        response = self.__initiate_GET(None, f'comments/{child_id}')
        comment_metadata = response[1]['data']['children']
        comments = []

        def retrieve_comments(child):
            body = child['data'].get('body', None)
            replies = child['data'].get('replies', None)
            if body:
                comments.append(body)
            if replies:
                nodes = replies['data']['children']
                for node in nodes:
                    retrieve_comments(node)

        for metadata in comment_metadata:
            if metadata['kind'] == REDDIT_COMMENT_TAG:
                retrieve_comments(metadata)
        return comments

    def fetch_reddit_data(self, listing, t=None, limit=DEFAULT_LIMIT):
        '''
        Fetches data from Reddit's API given the listing, and the time period
        to search if the listing is for top reddit posts.
        '''
        if not t and listing == 'top':
            raise ValueError(
                f"Cannot have listing {listing} while not specifying the time parameter {t}")

        subreddit_posts = self.get_reddit_posts(listing, t, limit)
        values = {column_name: [] for column_name in DATAFRAME_COLUMNS}
        for post in subreddit_posts:
            post_data: dict = post['data']
            post_comments: list[str] = self.fetch_comments(post_data['id'])

            values['Post_ID'].append(post_data['id'])
            values['Post_Title'].append(post_data['title'])
            values['Post_Subtext'].append(post_data['selftext'])
            values['Num_Comments_On_Post'].append(post_data['num_comments'])
            values['Comments'].append(post_comments)

        configured_dataframe = pd.concat(
            [self.dataframe, pd.DataFrame(values, columns=DATAFRAME_COLUMNS)],
            sort=False)

        self.dataframe = configured_dataframe.set_index(INDEX).dropna()


if __name__ == '__main__':
    # Example that implements a reddit request for r/madmen and obtains each post's data
    # within reasonable limits
    reddit_request = SubRedditRequest(False, "madmen")
    listings = ['hot', 'new', 'top', 'rising']
    times = ['hour', 'day', 'week', 'month', 'year', 'all']
    for listing in listings:
        if listing == 'top':
            for time in times:
                reddit_request.fetch_reddit_data(
                    "top", t=time, limit=DEFAULT_LIMIT)
        else:
            reddit_request.fetch_reddit_data(listing, limit=DEFAULT_LIMIT)
    reddit_request.dataframe.to_csv('madmen.csv')
