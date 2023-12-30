import json
import praw
import os
from dotenv import load_dotenv
load_dotenv()


APP_NAME = os.getenv("APP_NAME")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
SUBREDDIT = os.getenv("SUBREDDIT")

reddit = praw.Reddit(
    client_id= APP_ID,
    client_secret= APP_SECRET,
    user_agent=f"Window11:TestApp:v0.1 by {APP_NAME}",
)
subreddit = reddit.subreddit(SUBREDDIT)

def scrape_posts(NUM_COMMENTS=3, NUM_POSTS=25, MIN_WORDS=300):

    posts = []

    for submission in subreddit.top('all', limit=NUM_POSTS):
        try:
            submission.comments[NUM_COMMENTS - 1]
            score = submission.score
            # Post Information
            url = submission.url
            id = submission.id

            # Data
            question = submission.title
            context = submission.selftext
            url = submission.url

            comments = []
            comment_authors = []
            # Comments
            if submission.comments != None:
                idx = 0
                for comment in submission.comments:
                    try:
                        comment_text = comment.body
                        if len(comment_text) >= 5 * MIN_WORDS:
                            idx += 1
                            comment_author = comment.author.name
                            comment_url = comment.permalink
                            comment_text = comment.body
                            comments.append(comment_text)
                            comment_authors.append([comment_author, comment_url])
                    except:
                        pass
                    if idx == NUM_COMMENTS:
                            break
            if len(comments) > 0:
                posts.append([id, url, question, context, comments, comment_authors])
        except:
            continue
    return posts

def save_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f)