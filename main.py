import tkinter as tk
import requests
import webbrowser
import sqlite3
import time

base_url = "https://api.twitch.tv/helix"
client_id = "d1knruskmvex6wy0cdq6bu5fy2n5ov"
def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id
    }

def new_request(endpoint, token):
    request_url = f"{base_url}/{endpoint}"
    response = requests.get(request_url, headers=get_headers(token))
    response.raise_for_status()
    return response.json()["data"]

def get_user_id(name, token):
    user_id = new_request(f"users?login={name}", token)[0]["id"]
    return user_id
    
def get_followed_id(user_id, token):
    followed = new_request(f"streams/followed?user_id={user_id}", token)
    # return filter(lambda streamer: streamer['type'] == "live", followed)
    return followed

def post_device_auth():
    url = "https://id.twitch.tv/oauth2/device"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = "client_id=d1knruskmvex6wy0cdq6bu5fy2n5ov&scopes=user:read:follows"
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    webbrowser.open(response_json['verification_uri'])
    return response_json['device_code']

def retrieve_tokens(client_id, scopes, device_code):
    files = {
    'client_id': (None, client_id),
    'scopes': (None, scopes),
    'device_code': (None, device_code),
    'grant_type': (None, 'urn:ietf:params:oauth:grant-type:device_code'),
    }

    response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
    while response.status_code == 400:
        response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
        
    return response.json()['access_token']
 
connection = sqlite3.connect("auth.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS token (id INTEGER PRIMARY KEY, name TEXT, token TEXT)")

# Check access token at the start and not at every request, to prevent multiple calls to database
# Maybe move inside new request later, to get a new access token, if it expires
cursor.execute("SELECT * FROM token WHERE name = 'access_token'")
access_token = cursor.fetchone()

if access_token is None:
    device_code = post_device_auth()
    token = retrieve_tokens(client_id=client_id, scopes="user:read:follows", device_code=device_code)
    cursor.execute("INSERT INTO token (name, token) VALUES (?, ?)", ('access_token', token))
    connection.commit()

else:
    token = access_token[2]

connection.close()

while True:
    user_id = get_user_id('pixel_claw', token)
    followed = get_followed_id(user_id, token)
    live_streamers = list(map(lambda streamer: { streamer['user_name']}, followed))
    for streamer in live_streamers:
        print(streamer)
    print("<--------------------------------->")
    # time.sleep(5)

