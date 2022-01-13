from API_Codes import PASSWORD, USERNAME

HEADERS = {'User-Agent': 'MyBot/0.0.1'}
data = {'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD}

valid_get_listings = ["best",
                      "by_id/names",
                      "comments/article",
                      "controversial",
                      "duplicates/article",
                      "hot",
                      "new",
                      "random",
                      "rising",
                      "top",
                      "sort"]

DEFAULT_LIMIT = 25
REDDIT_API_URL = "https://oauth.reddit.com"
REDDIT_URL = "https://reddit.com"
REDDIT_ACCESS_TOKEN_LINK = 'https://www.reddit.com/api/v1/access_token'
REDDIT_COMMENT_TAG = 't1'
