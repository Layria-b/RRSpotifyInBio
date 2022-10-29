# by LameLexi#7004
# Enjoy :3

from recnetlogin import RecNetLogin
import requests
from twisted.internet import task, reactor
import spotipy
from spotipy.oauth2 import SpotifyOAuth

timeout = 60.0

# if you wanna add anything else to your bio besides what your currently playing put it here
recroom_bio = ''

#Rec Room Auth Stuff
USERNAME = ""
PASSWORD = ""

#Spotify Auth Stuff
client_id = ''
client_secret = ''
redirect_uri = ''
scope = "user-read-currently-playing"

rnl = RecNetLogin(username=USERNAME, password=PASSWORD)
token = rnl.get_token(include_bearer=True)

def get_current_song(scope, client_id, client_secret, redirect_uri):

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri)
    )

    spotify_resp = sp.current_user_playing_track()

    if spotify_resp['is_playing'] == False:
        return 'Nothing Right Now!'
    else:
        track_name = spotify_resp['item']['name']
        artists = [artist for artist in spotify_resp['item']['artists']]
        artist_names = ', '.join([artist['name'] for artist in artists])
        return f'{track_name} by {artist_names}!'

def rr_bio_change():
    rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
        data = {'bio':f"Listening To:\n{get_current_song(scope, client_id, client_secret, redirect_uri)}\n"} # if you wanna add more stuff to your bio add it after the '\n'
    )
    print(rec_resp)
    print(get_current_song(scope, client_id, client_secret, redirect_uri))
    pass

l = task.LoopingCall(rr_bio_change)
l.start(timeout)

reactor.run()
