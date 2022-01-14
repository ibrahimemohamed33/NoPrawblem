import requests
from Request_Constants import DEFAULT_LIMIT, REDDIT_ACCESS_TOKEN_LINK
from reddit_utils import initiate_GET, initiate_POST
from subreddit import SubRedditRequest


class Reddit:
    def __init__(self, client_id: str, client_secret: str, password: str,
                 user_agent: str, username: str) -> None:

        self.headers = self.__auth_headers(client_id=client_id,
                                           client_secret=client_secret,
                                           user_agent=user_agent,
                                           username=username,
                                           password=password)

    def __auth_headers(self, client_id: str, client_secret: str, password: str,
                       user_agent: str, username: str):
        '''
        Returns the authenticated headers to initiate requests
        '''
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        headers = {'User-Agent': user_agent}

        data = {'grant_type': 'password',
                'username': username,
                'password': password}

        OAuth_Post = requests.post(url=REDDIT_ACCESS_TOKEN_LINK,
                                   auth=auth,
                                   data=data,
                                   headers=headers)

        access_token = OAuth_Post.json()['access_token']
        return {**headers, **{'Authorization': f"bearer {access_token}"}}

    def search_subreddit_names(self, query: str, exact=False,
                               include_over_18=True):
        '''
        Finds subreddits whose names closely match the query
        '''
        params = {'exact': exact,
                  'include_over_18': include_over_18,
                  'query': query}

        return initiate_GET('/api/search_reddit_names', params=params)

    def subscribe_to_subreddits(self, subreddits: list, subscribe: bool):
        '''
        Subscribes or unsubscribes to the values in subreddits depending on the
        boolean subscribe
        '''
        action = 'sub' if subscribe else 'unsub'
        data = {'action': action,
                'sr_name': ', '.join(subreddits)}
        return initiate_POST('/api/subscribe', data=data)

    def get_subreddit_posts(self, subreddit_name: str, listing: str, t: str or None,
                            limit: int):
        '''
        Retrieves the subreddit posts of a specific subreddit
        '''
        subreddit = SubRedditRequest(subreddit_name=subreddit_name)
        return subreddit.get_reddit_posts(listing=listing, t=t, limit=limit)

    def subreddit_data(self, subreddit_name: str, listing: str, t=None,
                       limit=DEFAULT_LIMIT):
        '''
        Fetches the reddit data for a subreddit and listing (e.g., 'hot', 'new',
        'top', 'rising', etc.)
        '''
        subreddit = SubRedditRequest(subreddit_name=subreddit_name)
        return subreddit.fetch_subreddit_data(listing=listing,
                                              t=t,
                                              limit=limit)
