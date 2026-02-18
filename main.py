import tkinter as tk
import sqlite3

from api_requests import get_followed_id, get_users_by_id, get_tokens, get_user_by_name, retrieve_tokens
from web_image import WebImage

user_name = 'pixel_claw'
 
connection = sqlite3.connect("auth.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS token (user_name TEXT PRIMARY KEY, access_token TEXT, refresh_token TEXT)")

# Check access token at the start and not at every request, to prevent multiple calls to database
# Maybe move inside new request later, to get a new access token, if it expires
cursor.execute("SELECT * FROM token WHERE user_name = ?", [user_name])
saved_token = cursor.fetchone()

if saved_token is None:
    token = get_tokens()
    cursor.execute("INSERT INTO token (user_name, access_token, refresh_token) VALUES (?, ?, ?)", [user_name, token['access_token'], token['refresh_token']])
    access_token = token['access_token']
    connection.commit()

else:
    access_token = saved_token[1]

connection.close()

response = get_user_by_name(user_name, access_token)
if response.status_code == 401:
    connection = sqlite3.connect("auth.db")
    cursor = connection.cursor()
    refresh_token = saved_token[2]
    token = retrieve_tokens(scopes="user:read:follows", grant_type=refresh_token)
    cursor.execute("UPDATE token SET access_token = ?, refresh_token user_name = ?", [user_name, token['access_token'], token['refresh_token']])
    connection.close()
    access_token = token['access_token']
    response = get_user_by_name(user_name, access_token)

# receive streamer information
user_id = response.json()['data'][0]['id']
followed = get_followed_id(user_id, access_token).json()['data']
online_streamer_ids = list(map(lambda streamer: streamer['user_id'], followed))
streamer_user_info = get_users_by_id(online_streamer_ids, access_token)
profile_image_urls = list(map(lambda user: user['profile_image_url'],streamer_user_info))


root = tk.Tk()
for i, url in enumerate(profile_image_urls):
    img = WebImage(url).get()
    image_lab = tk.Label(root, image=img)
    image_lab.image = img
    image_lab.grid(row=i, column=0, sticky="N")


root.mainloop()