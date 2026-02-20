import tkinter as tk

from api_requests import get_followed_id, get_users_by_id, get_tokens, get_user_by_name, refresh_tokens, retrieve_tokens
from db_handler import auth
from web_image import WebImage

ROUTINE_SLEEP = 5000
# routine to get updated data
def get_streamer_routine(user_id, access_token):
    followed = get_followed_id(user_id, access_token).json()['data']
    online_streamer_ids = list(map(lambda streamer: streamer['user_id'], followed))
    streamer_user_info = get_users_by_id(online_streamer_ids, access_token)
    profile_image_urls = list(map(lambda user: user['profile_image_url'],streamer_user_info))

    for i, url in enumerate(profile_image_urls):
        img = WebImage(url).get()
        image_lab = tk.Label(main_frame, image=img)
        image_lab.image = img
        image_lab.grid(row=i, column=0, sticky="N")
    root.after(ROUTINE_SLEEP, get_streamer_routine, user_id, access_token)

def main():
    [response, access_token] = auth(user_name.get())
    # receive streamer information
    user_id = response.json()['data'][0]['id']
    init_frame.destroy()
    main_frame.tkraise()
    root.after(0, get_streamer_routine, user_id, access_token)
    

root = tk.Tk()
init_frame = tk.Frame(root)
init_frame.grid(row=0)
main_frame = tk.Frame(root)
main_frame.grid(row=0)
user_name_label = tk.Label(init_frame, text="User name: ")
user_name_label.grid(row=0)
user_name = tk.StringVar()
user_name_input = tk.Entry(init_frame, textvariable=user_name)
user_name_input.grid(row=0, column=1)
submit_button = tk.Button(init_frame, text="Submit", command=main)
submit_button.grid(row=1)
root.mainloop()