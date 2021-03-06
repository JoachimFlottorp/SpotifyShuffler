# Spotify Shuffler

This uses a shell like way of entering commands.

To use this you require a 'Spotify App' thing, basically you go to [Spotify-Dashboard](https://developer.spotify.com/dashboard/login).
Create a app. Once your 'Spotify App' has been made, enter its dashboard click the big green 'EDIT SETTINGS' button, scroll down 'Redirect URLs' and enter 'http://127.0.0.1:5273' This is so when you login spotify returns to this URL and we grab the token as a GET request.

## Client ID and Secret

Simply placing the keys in their respective places in the [.env](/.env) Allows the python script to read and use your keys.

### Instructions

1. First we run pip3 and install all the required packages.

    ```bash
    ~ pip3 install -r requirements.txt
    ```

2. Secondly we run the GetToken command, this asks spotify for your unique token, you will be instructed to login.

    ```bash
    ~ python3 SpotifyShuffler.py
    GetToken
    ```

3. Third we run the GetPlaylist command, this gets all playlists that you own with their respective id, we use this id in step 4.

    ```bash
    GetPlaylist
    ```

4. Lastly we run the Shuffle command using the playlist id as an argument, this shuffles the playlist into a new playlist.

     ```bash
    Shuffle 'token'
    ```
