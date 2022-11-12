from recnetlogin import RecNetLogin
import requests
from twisted.internet import task, reactor
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import os
from dotenv import load_dotenv
import sys

timeout = 60.0
song_compare = ''

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

load_dotenv()
config = configparser.ConfigParser()
config.read(resource_path("config.ini")) 

if config.getboolean('DEFAULT', 'storelogin') == True:
    YOURUSERNAME = os.environ['YOURUSERNAME']
    YOURPASSWORD = os.environ['YOURPASSWORD']
else:
    print('Enter the username/password of your account!')
    YOURUSERNAME = (input('Username: ')).lower()
    YOURPASSWORD = (input('Password: '))
    passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
    while passwordconfirm != 'y':
        YOURUSERNAME = (input('Username: ')).lower()
        YOURPASSWORD = (input('Password: '))
        passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
    storelogin = input('Would you like your login to be stored for next time(y/n)? ')
    while storelogin not in {'y', 'n'}:
        print('Enter y/n')
        storelogin = input('Would you like your login to be stored for next time(y/n)? ')
    if storelogin == 'y':
        config['DEFAULT']['storelogin'] = 'true'
        import dotenv
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)
        os.environ["YOURUSERNAME"] = YOURUSERNAME
        dotenv.set_key(dotenv_file, "YOURUSERNAME", os.environ["YOURUSERNAME"])
        os.environ["YOURPASSWORD"] = YOURPASSWORD
        dotenv.set_key(dotenv_file, "YOURPASSWORD", os.environ["YOURPASSWORD"])
        with open(resource_path("config.ini"), 'w') as configfile:
            config.write(configfile)
        
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-currently-playing'

bio = ''
bioconfirm = 'n'
def bioconfig(bioconfirm):
    while bioconfirm == 'n':
        bio = input('Enter any extra stuff you would like to add to your bio(press enter for none): ') 
        print('Listening to:')
        print('Example song by Example')
        print(bio)
        bioconfirm = input('Confirm you want your bio to this(y/n)?')
        while bioconfirm not in {'y', 'n'}:
            print('Enter y/n')
            bioconfirm = input('Confirm you want your bio to this(y/n)?')

    if bio not in {'', ' '}:
        savebio = input('Would you like the bio you entered to be saved next time you run the program(y/n)? ')
        while savebio not in {'y', 'n'}:
            print('Enter y/n')
            savebio = input('Would you like the bio you entered to be saved next time you run the program(y/n)? ')
        if savebio == 'y':
            import dotenv
            config['DEFAULT']['savebio'] = 'true'
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            os.environ["recroombio"] = bio
            dotenv.set_key(dotenv_file, "recroombio", os.environ["recroombio"])
        else:
            config['DEFAULT']['savebio'] = 'false'

    with open(resource_path("config.ini"), 'w') as configfile:
        config.write(configfile)

    return bio


if config.getboolean('DEFAULT', 'savebio') == False:
    bioconfig(bioconfirm)
elif config.getboolean('DEFAULT', 'savebio') == True: 
    print('Found saved bio!')
    print('Listening to:')
    print('Example song by Example')
    print(os.environ["recroombio"])
    bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    while bioconfirm not in {'y', 'n'}:
        print('Enter y/n')
        bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    if bioconfirm == 'n':
        bioconfig(bioconfirm)
    else: 
        bio = os.environ["recroombio"]

def login(YOURUSERNAME, YOURPASSWORD):
  rnl = RecNetLogin(username=YOURUSERNAME, password=YOURPASSWORD)
  token = rnl.get_token(include_bearer=True)
  return token
token = login(YOURUSERNAME, YOURPASSWORD)

def get_current_song(scope, client_id, client_secret, redirect_uri):

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri)
    )
    
    spotify_resp = sp.current_user_playing_track()

    try:
        track_name = spotify_resp['item']['name']
        artists = [artist for artist in spotify_resp['item']['artists']]
        artist_names = ', '.join([artist['name'] for artist in artists])
        song = f'{track_name} by {artist_names}!'
    except TypeError or spotify_resp['is_playing'] == False:
        song =  'Nothing Right Now!'
    return song

def rr_bio_change(token, bio):
    rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
    data = {'bio':f"Listening To:\n{get_current_song(scope, client_id, client_secret, redirect_uri)}\n{bio}"})
    if rec_resp.status_code == 401:
        token = login(YOURUSERNAME, YOURPASSWORD)
        rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
        data = {'bio':f"Listening To:\n{get_current_song(scope, client_id, client_secret, redirect_uri)}\n{bio}"})

    print(f'Currently playing song: {get_current_song(scope, client_id, client_secret, redirect_uri)}')
    print('Bio Change Success!')
    pass

l = task.LoopingCall(rr_bio_change, token, bio)
l.start(timeout)

reactor.run()