import sqlite3
from api_requests import get_tokens, get_user_by_name, refresh_tokens, retrieve_tokens

def auth(user_name):
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
        token = refresh_tokens(refresh_token)
        cursor.execute("UPDATE token SET access_token = ?, refresh_token = ? WHERE user_name = ?", [token['access_token'], token['refresh_token'], user_name])
        connection.close()
        access_token = token['access_token']
        response = get_user_by_name(user_name, access_token)
    return [response, access_token]