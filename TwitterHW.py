#Bradley Scharf
#SI 206 Discussion Section: Thursday 3PM

# Import statements
import unittest
import sqlite3
import requests
import json
import re
import tweepy
import twitter_info # still need this in the same directory, filled out
import datetime
import pytz

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# And we've provided the setup for your cache. But we haven't written any functions for you, so you have to be sure that any function that gets data from the internet relies on caching.
CACHE_FNAME = "twitter_cache.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

## [PART 1]

# Here, define a function called get_tweets that searches for all tweets referring to or by "umsi"
# Your function must cache data it retrieves and rely on a cache file!


def get_tweets():
    ##YOUR CODE HERE
    # check if our search term is already in the cache
    search_term = "umsi"
    if search_term in CACHE_DICTION:
            # return data from the cache
            print ("using cache")
            return CACHE_DICTION[search_term]
    else:
            # query twitter API for new data
            response = api.search(search_term)
            CACHE_DICTION[search_term] = response
            print ("fetching")
            return response
            # save that to the cache 


## [PART 2]
# Create a database: tweets.sqlite,
# And then load all of those tweets you got from Twitter into a database table called Tweets, with the following columns in each row:
## tweet_id - containing the unique id that belongs to each tweet
## author - containing the screen name of the user who posted the tweet (note that even for RT'd tweets, it will be the person whose timeline it is)
## time_posted - containing the date/time value that represents when the tweet was posted (note that this should be a TIMESTAMP column data type!)
## tweet_text - containing the text that goes with that tweet
## retweets - containing the number that represents how many times the tweet has been retweeted

# Below we have provided interim outline suggestions for what to do, sequentially, in comments.

# 1 - Make a connection to a new database tweets.sqlite, and create a variable to hold the database cursor.
sqlite_file = 'tweets.sqlite'
table_name = 'Tweets'

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


# 2 - Write code to drop the Tweets table if it exists, and create the table (so you can run the program over and over), with the correct (4) column names and appropriate types for each.
# HINT: Remember that the time_posted column should be the TIMESTAMP data type!
c.execute("drop table if exists Tweets");

c.execute('CREATE TABLE Tweets ( tweet_id INTEGER PRIMARY KEY, author TEXT, time_posted TIMESTAMP, tweet_text TEXT, retweets INTEGER )')
        

# 3 - Invoke the function you defined above to get a list that represents a bunch of tweets from the UMSI timeline. Save those tweets in a variable called umsi_tweets.

umsi_tweets = get_tweets()
# 4 - Use a for loop, the cursor you defined above to execute INSERT statements, that insert the data from each of the tweets in umsi_tweets into the correct columns in each row of the Tweets database table.

for t in umsi_tweets["statuses"]:
    tweet_id = t['id']
    author = t['user']['screen_name']
    format_str = "%a %b %d %H:%M:%S %z %Y"
    time_posted = datetime.datetime.strptime(t['created_at'], format_str)
    time_posted = time_posted.strftime("%Y-%m-%d %H:%M:%S")
    tweet_text = t['text']
    retweets = t['retweet_count']
    c.execute("INSERT INTO Tweets VALUES ( {i}, '{a}', '{tp}', '{tt}', {rt} ) "\
        .format(i = tweet_id, a = author, tp = time_posted, tt = tweet_text, rt = retweets))

#  5- Use the database connection to commit the changes to the database
conn.commit()

# You can check out whether it worked in the SQLite browser! (And with the tests.)

## [PART 3] - SQL statements
# Select all of the tweets (the full rows/tuples of information) from umsi_tweets and display the date and message of each tweet in the form:
    # Mon Oct 09 16:02:03 +0000 2017 - #MondayMotivation https://t.co/vLbZpH390b
    #
    # Mon Oct 09 15:45:45 +0000 2017 - RT @MikeRothCom: Beautiful morning at @UMich - It’s easy to forget to
    # take in the view while running from place to place @umichDLHS  @umich…
# Include the blank line between each tweet.

c.execute('SELECT * FROM Tweets')
all_rows = c.fetchall()
# print(all_rows)
for row in all_rows:
    # reformat our date
    format_str = "%Y-%m-%d %H:%M:%S" # matches e.g.  '2017-10-29 16:57:56'
    time_posted = datetime.datetime.strptime(row[2], format_str)
    time_posted = pytz.utc.localize(time_posted)
    time_posted = time_posted.strftime("%a %b %d %H:%M:%S %z %Y")
    print(time_posted, "-", row[3], "\n")
    
# Select the author of all of the tweets (the full rows/tuples of information) that have been retweeted MORE
# than 2 times, and fetch them into the variable more_than_2_rts.
# Print the results

c.execute('SELECT author FROM Tweets WHERE retweets > 2')
more_than_2_rts = c.fetchall()
print("Authors of tweets with more than 2 retweets:")
for info in more_than_2_rts:
    print(info[0])
        
conn.close()

if __name__ == "__main__":
    
    file_string = json.dumps(CACHE_DICTION)
    with(open(CACHE_FNAME, 'w')) as file:
        file.write(file_string)
    unittest.main(verbosity=2)
