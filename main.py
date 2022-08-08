import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
from flask import Flask, session, request, redirect
from flask_session import Session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

@app.route("/")
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True, client_id=cred.client_id, client_secret=cred.client_secret, redirect_uri=cred.redirect_url)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/top_songs">my top songs</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \
    # topSongs = get_top_songs()
    # short = topSongs[0]
    # mid = topSongs[1]
    # long = topSongs[2]
    # shortStr = "short term:     "
    # midStr = "mid term:     "
    # longStr = "long term:     "
    # for i in range(len(short)):
    #     shortStr = shortStr + str(i+1) + ": " + str(short[i]) + ",\t"
    #     midStr = midStr + str(i+1) + ": " + str(mid[i]) + ",\t"
    #     longStr = longStr + str(i+1) + ": " + str(long[i]) + ",\t"
    # return """<h1> Top Spotify Songs</h1>
    # <p>below shows your top ten most listened to songs over short, mid, and long terms</p><br><br> <form action="" method="get"> <input type="text" name="username"> <input type="submit" value="username"><br><br>""" + shortStr + """<br><br>""" + midStr + """<br><br>""" + longStr

@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler, client_id=cred.client_id, client_secret=cred.client_secret, redirect_uri=cred.redirect_url)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler, client_id=cred.client_id, client_secret=cred.client_secret, redirect_uri=cred.redirect_url)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."

@app.route('/top_songs')
def get_top_songs():
    scope = 'user-top-read'
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler, client_id=cred.client_id, client_secret=cred.client_secret, redirect_uri=cred.redirect_url)
    # if not auth_manager.validate_token(cache_handler.get_cached_token()):
    #     return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)

    ranges = ['short_term', 'medium_term', 'long_term']
    short = []
    mid = []
    long = []
    total = [short, mid, long]

    for sp_range in ranges: 
        results = sp.current_user_top_tracks(time_range=sp_range, limit=10)
        for i, item in enumerate(results['items']):
            if(len(short) < 10):
                short.append(item['name'])
            elif(len(mid) < 10):
                mid.append(item['name'])
            elif(len(long) < 10):
                long.append(item['name'])
    shortStr = "short term:     "
    midStr = "mid term:     "
    longStr = "long term:     "
    for i in range(len(short)):
        shortStr = shortStr + str(i+1) + ": " + str(short[i]) + ",\t"
        midStr = midStr + str(i+1) + ": " + str(mid[i]) + ",\t"
        longStr = longStr + str(i+1) + ": " + str(long[i]) + ",\t"
    return """<h1> Top Spotify Songs</h1>
    <p>below shows your top ten most listened to songs over short, mid, and long terms</p><br><br> <form action="" method="get"> <input type="text" name="username"> <input type="submit" value="username"><br><br>""" + shortStr + """<br><br>""" + midStr + """<br><br>""" + longStr

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)