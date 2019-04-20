import json
from flask import Flask, request
import requests
from subprocess import run
import base64
from crontab import CronTab
from playlists import playlists

app = Flask(__name__)

#  Client Keys
CLIENT_ID = "7e1cc7ca19974c4ba5e904e5c20784ac"
CLIENT_SECRET = "7205a4e9e27f49b1b689e532a1bb5801"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAY_URL = SPOTIFY_API_BASE_URL+"/me/player/play"


# App's global variables
SYSTEM_USER = "pi" # janek
PI_DEVICE_ID = "638c4613fba455726772c486cba9acc0775f49e"
REF_TOKEN = "AQC3-yi9SWBAyja3DmcRDJHoV1oz-jK-aFlPo-OqtjCDHUZQExt153nwidgbKMOt-GTAGxJJqo-pwvSFXn5Rag_ZArY5HX4uB0DfNdZVE-LuHsTecLIqr-iEbn3u8bmuSPpnZA"
ALARM_ADNOTATION_TAG = "SPOTI-ALARM" # Identifies lines in crontab created by this program (and not other users/programs)
RADIO_STREAM_URL = "http://radioluz.pwr.edu.pl:8000/luzlofi.ogg"
HOSTNAME = "0.0.0.0"
PORT = 3141
ADDRESS = HOSTNAME + ":" + str(PORT)

@app.route("/spotiauth")
def spotiauth():
    # Ask for a new access token, using the refresh token, CLIENT_ID and CLIENT_SECRET. Save it to a file.
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REF_TOKEN
    }

    auth_str = '{}:{}'.format(CLIENT_ID,CLIENT_SECRET)
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(b64_auth_str)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    file = open("access_token.txt","w")
    file.write(access_token)
    file.close()

    return access_token

@app.route("/spotiplay")
def spotiplay():
    response = play(spotify_uri="spotify:album:5uiLjgmdPV4dgamvmC64Oq")

    # #TODO:
    # if response.error != None:
    #     print("ERROR: " + response.error)
    #     print("Retrying...") 
    #     token = spotiauth()
    #     spotiplay(token)
    return "SPOTIPLAY, RESPONSE: " + response.text


def play(spotify_uri = "spotify:album:5uiLjgmdPV4dgamvmC64Oq", song_number=0, access_token=None): #XXX: naming problem between this and spotiplay
    if access_token == None:
        file = open("access_token.txt","r")
        access_token = file.read()
        file.close()
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    data = '{"context_uri":"' + spotify_uri + '","offset":{"position":' + str(song_number) + '},"position_ms":0}'
    url_params = []
    # url_params = {"device_id":"638c4613fba455726772c486cba9acc0775f49e"}   
    response = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers, data=data, params=url_params) 
    return response


@app.route("/radioplay")
def radioplay():
    run(["omxplayer", RADIO_STREAM_URL])
    return "LUZ"


@app.route('/cronsave', methods = ['POST'])
def cronsave():
    minutes = request.json['minutes']
    hours = request.json['hours']
    music_mode = request.json['mode']
    if music_mode == "luz":
        command = "curl " + ADDRESS + "/radioplay"
    else:
        command = "curl " + ADDRESS + "/spotiauth && curl " + ADDRESS + "/spotiplay"
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ADNOTATION_TAG)
    job = cron_raspi.new(command=command, comment=ALARM_ADNOTATION_TAG)
    job.minute.on(minutes)
    job.hour.on(hours)
    cron_raspi.write()
    return "OK"

@app.route('/cronclean', methods = ['GET'])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ADNOTATION_TAG)
    cron_raspi.write()
    return "CLEANED"

@app.route('/areyourunning', methods = ['GET'])
def areyourunning():
    return "YES"

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')