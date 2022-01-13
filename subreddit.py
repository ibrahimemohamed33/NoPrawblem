import pandas as pd
from Request_Constants import *
from reddit_utils import *

DATAFRAME_COLUMNS = ['Post_ID', 'Post_URL', 'Post_Title', 'Post_Subtext',
                     'Num_Comments_On_Post', 'Comments']

INDEX = DATAFRAME_COLUMNS[0]


class SubRedditRequest:
    def __init__(self, subreddit_name: str) -> None:
        '''
        Initializes the Reddit Request class

        Inputs:
            subreddit_name: the name of the subreddit
            is_username: whether the name is a username or a subreddit page
        '''
        self.subreddit = subreddit_name
        self.dataframe = pd.DataFrame(
            columns=DATAFRAME_COLUMNS).set_index(INDEX)

    def __initiate_GET(self, params: dict or None, *args):
        '''
        Initiates a GET request to Reddit's API relating to subreddit endpoints
        '''
        endpoint = extend_url('/r', self.subreddit, args)
        return initiate_GET(endpoint, params=params)

    def subscribe(self):
        '''
        Subscribes to the subreddit
        '''
        return self.subscribe_to_subreddits([self.subreddit], True)

    def unsubscribe(self):
        '''
        Unsubscribes to the subreddit
        '''
        return self.subscribe_to_subreddits([self.subreddit], False)

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
            '''
            Recursive function that retrieves each comment in a child post
            and traverses each node
            '''
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

    def fetch_reddit_data(self, listing, t=None, limit=DEFAULT_LIMIT) -> None:
        '''
        Fetches data from Reddit's API given the listing, and the time period
        to search if the listing is for top reddit posts.
        '''
        if not t and listing == 'top':
            raise ValueError(
                f"Cannot have listing {listing} while not specifying a time parameter")

        subreddit_posts = self.get_reddit_posts(listing, t, limit)
        values = {column_name: [] for column_name in DATAFRAME_COLUMNS}
        for post in subreddit_posts:
            post_data: dict = post['data']
            post_id = post_data['id']
            post_comments: list[str] = self.fetch_comments(post_id)
            post_url = extend_url(REDDIT_URL, 'r', self.subreddit, 'comments',
                                  post_id)

            values['Post_ID'].append(post_id)
            values['Post_URL'].append(post_url)
            values['Post_Title'].append(post_data['title'])
            values['Post_Subtext'].append(post_data['selftext'])
            values['Num_Comments_On_Post'].append(post_data['num_comments'])
            values['Comments'].append(post_comments)

        dataframe = pd.DataFrame(values, columns=DATAFRAME_COLUMNS)
        configured_dataframe = pd.concat([self.dataframe, dataframe.set_index(INDEX)],
                                         sort=False)

        self.dataframe = configured_dataframe


if __name__ == '__main__':
    # Example that implements a reddit request for r/madmen and obtains each post's data
    # within reasonable limits
    subreddit = SubRedditRequest("madmen")
    listings = ['hot', 'new', 'top', 'rising']
    times = ['hour', 'day', 'week', 'month', 'year', 'all']
    for listing in listings:
        if listing != 'top':
            subreddit.fetch_reddit_data(listing)
        else:
            for time in times:
                subreddit.fetch_reddit_data(listing, time)

    subreddit.dataframe.to_csv('madmen.csv')
