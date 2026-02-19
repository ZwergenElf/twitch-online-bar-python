import tkinter as tk

from api_requests import get_followed_id, get_users_by_id, get_tokens, get_user_by_name, refresh_tokens, retrieve_tokens
from db_handler import auth
from web_image import WebImage

ROUTINE_SLEEP = 5000
# routine to get updated data
def get_streamer_routine():
    followed = get_followed_id(user_id, access_token).json()['data']
    online_streamer_ids = list(map(lambda streamer: streamer['user_id'], followed))
    streamer_user_info = get_users_by_id(online_streamer_ids, access_token)
    profile_image_urls = list(map(lambda user: user['profile_image_url'],streamer_user_info))

    for i, url in enumerate(profile_image_urls):
        img = WebImage(url).get()
        image_lab = tk.Label(root, image=img)
        image_lab.image = img
        image_lab.grid(row=i, column=0, sticky="N")
    root.after(ROUTINE_SLEEP, get_streamer_routine)


user_name = 'pixel_claw'

[response, access_token] = auth(user_name)
# receive streamer information
user_id = response.json()['data'][0]['id']

root = tk.Tk()
root.after(0, get_streamer_routine)
root.mainloop()