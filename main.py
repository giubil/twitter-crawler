import random
import json
import time
import os

import model_datastore as model

from twitterApi import TwitterApi
from config import *

def main():
    random.seed()
    users_file = open("users.json", "r")
    users_array = json.load(users_file)
    users_file.close()
    obj = TwitterApi(TOKEN, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    while True:
        for user in users_array:
            user_key, stored_user = obj.get_user_from_db(user["name"])
            if stored_user is not None:
                obj.update_tweets(user_key, user["name"], user["banned_words"],
                                  model.from_datastore(stored_user)["id"])
            else:
                obj.first_analyse(user["name"], user["banned_words"])
        print("Sleeping before next update round")
        time.sleep(900)


if __name__ == "__main__":
    main()
