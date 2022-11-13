from recnetlogin import RecNetLogin
import requests
from twisted.internet import task, reactor
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import os
from dotenv import load_dotenv

timeout = 60.0

load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")

if config.getboolean('LOGIN', 'storelogin') == True:
    YOURUSERNAME = config['LOGIN']['YOURUSERNAME']
    YOURPASSWORD = config['LOGIN']['YOURPASSWORD']
    use_found_login = input('Found login would you like to use?')
    while use_found_login not in {'y', 'n'}:
        print('Enter y/n')
        use_found_login = input('Found login would you like to use?')
    if use_found_login == 'n': 
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
            config['LOGIN']['storelogin'] = 'true'
            config['LOGIN']['YOURUSERNAME'] = YOURUSERNAME
            config['LOGIN']['YOURPASSWORD'] = YOURPASSWORD
            with open("config.ini", 'w') as configfile:
                config.write(configfile)
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
        config['LOGIN']['storelogin'] = 'true'
        config['LOGIN']['YOURUSERNAME'] = YOURUSERNAME
        config['LOGIN']['YOURPASSWORD'] = YOURPASSWORD
        with open("config.ini", 'w') as configfile:
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
            config['BIO']['savebio'] = 'true'
            config['BIO']['bio'] = bio
        else:
            config['BIO']['savebio'] = 'false'

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    return bio

config.read("config.ini")

if config.getboolean('BIO', 'savebio') == False:
    bio = bioconfig(bioconfirm)
elif config.getboolean('BIO', 'savebio') == True: 
    print('Found saved bio!')
    print('Listening to:')
    print('Example song by Example')
    print(config['BIO']['bio'])
    bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    while bioconfirm not in {'y', 'n'}:
        print('Enter y/n')
        bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    if bioconfirm == 'n':
        bioconfig(bioconfirm)
    else: 
        bio = config['BIO']['bio']

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
