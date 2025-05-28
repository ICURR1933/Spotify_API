from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, redirect, request
import urllib.parse
import webbrowser

app = Flask(__name__)
app.secret_key = "1933w606-22p773-5691706"

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_id = os.getenv("USER_ID")
redirect_uri = os.getenv("REDIRECT_URI")


#Creating Playlist With Spotify
def create_playlist(access_token):
    playlist_name = input("What would you like to name your new playlist?:")
    # Get user's profile to fetch user_id
    user_profile = get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    user_id = user_profile.get('id')
    if not user_id:
        return f"Failed to get user ID: {user_profile}"

    # Create a new playlist with user input
    playlist_data = {
        'name': playlist_name,
        'description': "Created via using Inigo's code",
        'public': False  
    }
    headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    playlist_response = post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers=headers,
        json=playlist_data
    )

    result = playlist_response.json()

    if playlist_response.status_code == 201:
        return f"{playlist_name} playlist created successfully! <br><a href='{result['external_urls']['spotify']}'>Open on Spotify</a>"
    else:
        return f"Failed to create playlist: {result}"

@app.route('/')

def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify"

@app.route('/login')
def login():
    scope = "user-read-private user-read-email playlist-modify-private"

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
        "show_dialog" : True
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    #return f"Authorization code received: <code>{code}</code>"

    if not code:
        return "No code received"

    # Prepare basic auth header
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = post(token_url, data=payload, headers=headers)
    data = response.json()

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    if not access_token:
        return f"Error retrieving token: {data}"

    # Store the token or pass it to the next step
    return create_playlist(access_token)


if __name__ == "__main__":
    webbrowser.open('http://127.0.0.1:8888/callback')
    app.run(host="0.0.0.0", port=8888, debug=True)

#if __name__ == "__main__":
    #app.run(host="0.0.0.0", debug=True)