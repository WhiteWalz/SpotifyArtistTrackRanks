import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import io
import billboard
import time
import requests
from Variables import CLIENT_ID, CLIENT_SECRET

def run():
    client_cred_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    artistURL = input("Please enter the url of the artist desired: ")
    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)
    sp.trace = False
    get_albums(sp.artist(artistURL), sp)

def get_albums(artist, sp):
    fil = open(artist['name']+'_ranks.txt', 'w')
    charts = get_charts('hot-100')
    albums = []
    results = sp.artist_albums(artist['id'], 'album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    results = sp.artist_albums(artist['id'], 'single')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    u = set()
    u2 = set()
    for album in albums:
        name = album['name'].upper()
        if not name in u:
            u.add(name)
            get_tracks(album, sp, fil, u2, charts)
    
def get_tracks(album, sp, saveFile, u2, charts):
    tracks = []
    results = sp.album_tracks(album['id'])
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    for track in tracks:
        flag = 1
        trueTrack = sp.track(track['id'])
        if not track['name'] in u2:
            u2.add(track['name'])
            flag = 0
        saveFile.write(track['name'] + '\t' + album['name'] +'\t' + str(len(track['available_markets'])) + '\t'
        + album['release_date'] + '\t' + str(trueTrack['popularity'])
        + '\t' + get_billboard(track['name'], 'hot-100', flag, charts) + '\n')

def get_billboard(name, chartName, flag, charts):
    if flag:
        return 'See other song listing'
    """chart = billboard.ChartData(chartName)"""
    """while chart.previousDate and index < 1040:
        for song in chart:
            if song.title == name:
                return str(song.peakPos) + '(' + str(song.weeks) + ')'"""
    for chart in charts:
        for song in chart.entries:
            if song.title == name:
                return str(song.peakPos) + '(' + str(song.weeks) + ')'
    return 'Song never made ' + chartName
    
def get_charts(chartName):
    charts = []
    index = 0
    chart = billboard.ChartData(chartName)
    while chart.previousDate and index < 1600:
        charts.append(chart)
        print(chart.date + '\n')
        try:
            chart = billboard.ChartData(chartName, chart.previousDate, timeout=None)
        except requests.exceptions.HTTPError:
            print('HTTP Error encountered. Stopping chart parsing at' + chart.date)
            return charts
        time.sleep(7)
        index += 1
    return charts

if __name__ == "__main__":
    run()