import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred

scope = 'user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_id, client_secret=cred.client_secret, redirect_uri=cred.redirect_url, scope=scope, cache_handler=spotipy.MemoryCacheHandler()))

ranges = ['short_term', 'medium_term', 'long_term']

for sp_range in ranges:
    print("range:", sp_range)
    results = sp.current_user_top_tracks(time_range=sp_range, limit=10)
    for i, item in enumerate(results['items']):
        print(i, item['name'], '//', item['artists'][0]['name'])
    print()