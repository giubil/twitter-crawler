# Twitter Crawler

This is a crawler that will crawl tweets of an user supplied in a userlist, will keep only text tweets (i.e. no tweets containing an image or a video), remove tweets that contains banned words (such as the name) and put them in a Google Datastore.

This application is made to run on a Google Container Engine with access to a Google Datastore.

## Requirements

If run on Google Container Engine, gcloud, kubectl and docker are required

If run locally, Python 3.x, pip, gcloud, Java JRE (version 7 or higher) and gcloud datastore emulator are required.
Virtualenv is recomended.

## Installation

For both types of installation you will first need to add your api keys and project id in config.py.

You can get twitter api keys here : [Twitter Apps](https://apps.twitter.com/)

Your project id can be found in the [Google Cloud Console](https://console.cloud.google.com/)

For both types of deployments, you will need to setup the users.json file. This file contains a json representation of the users that you will crawl, as well as the banned words for this user's tweets.

To do that, you will need to run the `add_new_user.py` script :

`python add_new_user.py`

The program will then ask you to enter the twitter handle of that user, and then a list of banned words, space separated.

To exit the program, just enter a blank twitter handle.

### Deployment on Google Container Engine

This assumes that you have Google Cloud environement with the requirements set up. If not, please follow this guide : [Setting up gcloud](https://cloud.google.com/sdk/gcloud/)

To deploy this application on a Google Container Engine, you will first need to build the Docker image : 

```docker build -t gcr.io/$project-id/tweets-crawler:v1 .```

Then push it to Google Container Registry :

```gcloud docker -- push gcr.io/$project-id/tweets-crawler:v1```

You will then need to create a new Container Engine cluster, and grant it access to the Datastore :

```
gcloud container clusters create hello-tweets \
  --scopes "https://www.googleapis.com/auth/userinfo.email","cloud-platform" \
  --num-nodes 2
```

Wait for a few minutes while the cluster is starting.

You will then need to get the credentials to user `kubectl``

`gcloud container clusters get-credentials hello-tweets`

You can then use `kubectl` to run your Docker image on the Container Engine :

`kubectl run hello-tweets --image=gcr.io/$project-id/tweets-crawler:v1`

Congratulation, your container is up and runnning.

If you wish to clean up and delete the kubectl deployment, run the following command :

`kubectl delete deployment hello-tweets`

To delete the Container Engine cluster :

`gcloud container clusters delete hello-tweets`

### Local deployment

If you wish to use a Virtualenv please run the following command :

`mkdir venv && virtualenv venv && source ./venv/bin/activate`

You will then need to install the Python dependencies :

`pip install -r requirements.txt`

Then you will need to start the Datastore emulator :

`gcloud beta emulators datastore start`

In an other terminal, source the Datastore Emulator env variables : 

`$(gcloud beta emulators datastore env-init)`

You can then run the main program by executing :

`python main.py`
