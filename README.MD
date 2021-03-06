# No Praw? No Prawblem

This repository is an implementation of some of the more useful features of connecting to the [Reddit API](https://www.reddit.com/dev/api/) without using PRAW. It was initially created just to receive all the comments under a subreddit, like those for _r/madmen_ or _r/algotrading_, in hopes of training a neural network. However, there were a few functions in the API I found immensely useful.

## Getting Started

Once you have your username, password, client secret code, and script code, simply run these two commands:

```python
import nopraw 
reddit = nopraw.Reddit(username=YOUR_USERNAME,
                       password=YOUR_PASSWORD, 
                       client_secret=YOUR_SECRET_CODE, 
                       client_id=YOUR_CLIENTID, 
                       user_agent='MyBot')
```

## Example
**_NoPrawblem_** supports retrieving some of the more important data within current Reddit posts. These include each post's ID, public URL, title, subtext, and comments. For example, to retrieve (up to a limit of 25 in this example) the new, hot, and top posts, we run the command:

```python
reddit.subreddit_posts_data('madmen', ['hot', 'new', 'top'], times=['week'])
```

In doing so, you get a dataframe like the one in Images/dataframe.png
![dataframe](/Images/dataframe.png)

When looking at the first result of the dataframe, for example, we get
![example](/Images/example.png)

This matches the reddit post here
![reddit](/Images/reddit.png)
