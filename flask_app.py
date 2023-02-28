from flask import Flask, render_template, request

import folium
from dotenv import load_dotenv
import os
import base64
import requests
import json
import pandas as pd

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Contept-Type": "application/x-www-form-unlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data, timeout = 100)
    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

def search_fo_countries(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"

    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"][0]["album"]["available_markets"]
    
    return json_result

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = requests.get(url, headers= headers)
    json_result = json.loads(result.content)['tracks'][0]['album']['name']

    return json_result

def spotify_json(token, artist_name):
    url = "https://api.spotify.com/v1/search/"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    result = requests.get(query_url, headers = headers)
    json_result = json.loads(result.content)

    best_track = get_songs_by_artist(token, json_result['artists']['items'][0]['id'])
    countries = search_fo_countries(token, best_track)
    
    return countries

def read_file():
    df = pd.read_csv("countries.csv")

    return df

def create_map(artist):
    """
    Create map
    """
    map = folium.Map(tiles="Stamen Terrain")

    fg = folium.FeatureGroup(name="songs")
    countries = spotify_json(get_token(), artist)

    df = read_file()
    for index, _ in enumerate(countries):
        latitude = df._get_value(index, 'latitude')
        longitude = df._get_value(index, 'longitude')
        fg.add_child(folium.Marker(location=[int(latitude), int(longitude)],
                                    popup = df._get_value(index, 'name'),
                                    icon=folium.Icon(color="black", icon_size = (38, 95))))

    map.add_child(fg)
    map.add_child(folium.LayerControl())
    return map.get_root().render()

app = Flask(__name__)
@app.route("/")
@app.route("/home")
def home():
    return render_template('input_page.html')

@app.route("/search_countries", methods = ['POST'])
def search():
    artist = request.form['artist']
    return create_map(artist)
app.run(debug=True)