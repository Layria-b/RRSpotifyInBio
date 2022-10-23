# by LameLexi#7004
# Enjoy :3

from recnetlogin import RecNetLogin
import requests
from twisted.internet import task, reactor


timeout = 60.0

USERNAME = ""
PASSWORD = ""
ACCESS_TOKEN = ''

rnl = RecNetLogin(username=USERNAME, password=PASSWORD)
token = rnl.get_token(include_bearer=True)

URL = 'https://api.spotify.com/v1/me/player/currently-playing'
def get_current_song(ACCESS_TOKEN):
    try: 
        vr_resp = requests.get(URL, 
            headers={
            "Authorization": f'Bearer {ACCESS_TOKEN}'}
        )
    except KeyError:
        print("error")
        exit()
    
    json_vr_resp = vr_resp.json()
    track_name = json_vr_resp['item']['name']
    artists = [artist for artist in json_vr_resp['item']['artists']]
    artist_names = ', '.join([artist['name'] for artist in artists])
    return f"{track_name} by {artist_names}"

def rr_bio_change():
    rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
        data = {'bio':f"Listening to:\n{get_current_song(ACCESS_TOKEN)}"}
    )
    print(rec_resp)
    print(get_current_song(ACCESS_TOKEN))
    pass

l = task.LoopingCall(rr_bio_change)
l.start(timeout)

reactor.run()
