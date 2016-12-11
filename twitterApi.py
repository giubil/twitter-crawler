import random
import sys

from twitter import OAuth, Twitter

import model_datastore as model

class TwitterApi():
    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        self._twitter_instance = Twitter(
            auth=OAuth(token, token_secret, consumer_key, consumer_secret))

    def _get_user_data(self, screen_name):
        "Get data about the user"
        print(screen_name)
        data = self._twitter_instance.statuses.user_timeline(
            screen_name=screen_name, count=1)
        data = data[0]["user"]
        data = {
            "id": data["id"],
            "profile_image": data["profile_image_url_https"].replace("_normal", ""),
            "name": data["name"],
            "screen_name": data["screen_name"]}
        return data

    def _get_all_timeline(self, screen_name, since_id=None):
        """Returns the timeline of an user
        If since_id is set, will get new tweets instead of the whole timeline"""
        if since_id is not None:
            data = self._twitter_instance.statuses.user_timeline(
                screen_name=screen_name, count=200, trim_user=True, since_id=since_id)
        else:
            data = self._twitter_instance.statuses.user_timeline(
                screen_name=screen_name, count=200, trim_user=True)
        while len(data) >= 200:
            print("For user {0} we are at {1} tweets".format(screen_name, str(len(data))))
            last_id = data[-1]["id"]
            if since_id is not None:
                _ = self._twitter_instance.statuses.user_timeline(
                    screen_name=screen_name, count=200, trim_user=True,
                    max_id=last_id, since_id=since_id)
            else:
                _ = self._twitter_instance.statuses.user_timeline(
                    screen_name=screen_name, count=200, trim_user=True,
                    max_id=last_id)
            if len(_) == 1:
                break
            data += _
        return data

    def _extract_data(self, tweet_list):
        """Extract relevent data from tweets"""
        new_data = []
        for tweet in tweet_list:
            new_data.append({
                "id": tweet["id"],
                "text": tweet["text"],
                "retweet_count": tweet["retweet_count"],
                "favorite_count": tweet["favorite_count"]})
        return new_data

    def _clean_tweets(self, data, not_in_tweet):
        "Cleans tweets and removes images retweet etc"
        new_list = []
        for tweet in data:
            if (not "media" in tweet['entities'] and
                    len(tweet["entities"]["urls"]) == 0 and
                    len([x for x in not_in_tweet if x.lower() in tweet["text"].lower()]) == 0):
                new_list.append(tweet)
        data = new_list
        return new_list

    def _get_high_retweets(self, tweets_list, length=50):
        "Gets the highest retweeted tweets of length LENGTH"
        return sorted(tweets_list, key=lambda k: k['retweet_count'], reverse=True)[:length]

    def _save_tweet(self, id_user, id_tweet, data):
        "Save tweet with an user as its ancestor"
        ds = model.get_client()
        key = ds.key('celebUser', id_user, 'celebTweet', id_tweet)
        entity = model.datastore.Entity(key=key,)
        entity.update(data)
        ds.put(entity)

    def _get_user_latest_tweet_id_in_db(self, user_key):
        ds = model.get_client()
        query = ds.query(kind="celebTweet", ancestor=user_key)
        results = list(query.fetch())
        highest_tweet = None
        for res in results:
            _ = model.from_datastore(res)
            if highest_tweet is None or _["id"] > highest_tweet["id"]: #There is no error with highest_tweet, it's just the linter not knowing what I am doing
                highest_tweet = _
        return highest_tweet["id"]

    def _get_whole_timeline_from_db(self, user_key):
        ds = model.get_client()
        query = ds.query(kind="celebTweet", ancestor=user_key)
        results = list(query.fetch())
        res_transformed = []
        for res in results:
            res_transformed.append(model.from_datastore(res))
        return res_transformed

    def _get_tweets_to_delete(self, full_list, pushable_list):
        "Will get the tweets that got deranked from the db to delete them"
        tweets_to_delete = []
        for tweet in full_list:
            if tweet not in pushable_list:
                tweets_to_delete.append(tweet)
        return tweets_to_delete

    def _delete_tweets(self, twet_list):
        "Delete tweets from the database"
        ds = model.get_client()
        for tweet in twet_list:
            key = ds.key("celebTweet", tweet["id"])
            ds.delete(key)

    def first_analyse(self, screen_name, banned_keywords):
        """Get user details, whole user timeline, and save them in DB"""
        print("Starting for user " + screen_name)
        user_data = self._get_user_data(screen_name)
        user_data["random"] = random.randint(0, sys.maxsize)
        _ = self._get_all_timeline(screen_name)
        print("Whole timeline length {}".format(len(_)))
        _ = self._clean_tweets(_, banned_keywords)
        _ = self._extract_data(_)
        timeline = self._get_high_retweets(_)
        user_id = user_data["id"]
        del user_data["id"]
        model.create(user_data, "celebUser", id=user_id)
        print("Saving {} tweets".format(len(timeline)))
        for tweet in timeline:
            tweet_id = tweet["id"]
            del tweet["id"]
            self._save_tweet(user_id, tweet_id, tweet)

    def get_user_from_db(self, screen_name):
        "Check if user is already present in the database"
        ds = model.get_client()
        user_data = self._get_user_data(screen_name)
        key = ds.key('celebUser', user_data["id"])
        res_user = ds.get(key)
        print(screen_name, res_user)
        return key, res_user

    def update_tweets(self, user_key, screen_name, banned_keywords, user_id):
        "Will get the latest tweets in db, get all the tweets posted after that and update the db"
        latest_id = self._get_user_latest_tweet_id_in_db(user_key)
        _ = self._get_all_timeline(screen_name, since_id=latest_id)
        if len(_) == 0: # If there are no new tweets, stop here
            return
        _ = self._clean_tweets(_, banned_keywords)
        _ = self._extract_data(_)
        _ += self._get_whole_timeline_from_db(user_key)
        timeline = self._get_high_retweets(_)
        self._delete_tweets(self._get_tweets_to_delete(_, timeline))
        print("Saving {} tweets to update db".format(len(timeline)))
        for tweet in timeline:
            tweet_id = tweet["id"]
            del tweet["id"]
            self._save_tweet(user_id, tweet_id, tweet)

