
import requests
import webbrowser

base_url = "https://api.twitch.tv/helix"
client_id = "d1knruskmvex6wy0cdq6bu5fy2n5ov"
client_secret = "or9sq1dxdjc9ppu0xbwnlsi1lv88eh"

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id
    }

def get_request(endpoint, token):
    request_url = f"{base_url}/{endpoint}"
    try:
        response = requests.get(request_url, headers=get_headers(token))
        if response.status_code != 401:
            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred:", e)

    return response
    

def get_user_by_name(name, token):
    response = get_request(f"users?login={name}", token)
    return response
    
def get_followed_id(user_id, token):
    followed = get_request(f"streams/followed?user_id={user_id}", token)
    return followed

def get_users_by_id(user_ids, token):
    user_ids_parameter = "id=" + "&id=".join(user_ids)
    response = get_request(f"users?{user_ids_parameter}", token)
    return response.json()['data']

def post_device_auth():
    url = "https://id.twitch.tv/oauth2/device"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = f"client_id={client_id}&scopes=user:read:follows"
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    webbrowser.open(response_json['verification_uri'])
    return response_json['device_code']

def retrieve_tokens(scopes, grant_type = 'urn:ietf:params:oauth:grant-type:device_code'):
    device_code = post_device_auth()
    files = {
    'client_id': (None, client_id),
    'scopes': (None, scopes),
    'device_code': (None, device_code),
    'grant_type': (None, grant_type),
    }

    response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
    while response.status_code == 400:
        response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
        
    return response.json()

def refresh_tokens(refresh_token):
    files = {
    'client_id': (None, client_id),
    'client_secret': (None, client_secret),
    'refresh_token': (None, refresh_token),
    'grant_type': (None, "refresh_token"),
    }

    response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
    while response.status_code == 400:
        response = requests.post('https://id.twitch.tv/oauth2/token', files=files)
        
    return response.json()

def get_tokens():
    return retrieve_tokens(scopes="user:read:follows")