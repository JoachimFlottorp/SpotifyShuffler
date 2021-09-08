from enum import IntEnum
import requests
from requests.exceptions import HTTPError
from colorama import init
import json
import random
import base64
import webbrowser
import urllib.parse
import math

# https://developer.spotify.com/documentation/web-api/

class StatusCode(IntEnum):
    Ok = 200,
    Created = 201,
    Accepted = 202,
    NoContent = 204,
    NotModified = 304,
    BadRequest = 400,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
    TooManyRequests = 429,
    InternalServerError = 500,
    BadGateway = 502,
    ServiceUnavailable = 503

class ErrorStatusCode(IntEnum):
    BadRequest = 400,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
    TooManyRequests = 429,
    InternalServerError = 500,
    BadGateway = 502,
    ServiceUnavailable = 503

class HTTPMethod:
    GET = 0,
    PUT = 1,
    POST = 2,
    NOREDIRECT = 3,

class bcolors:
    OKGREEN = '\033[32m'
    WARNING = '\033[31m'
    ENDC = '\033[0m'

class SpotifyShuffler:
    token = None
    tokenIsSet = False
    def __init__(self):
        # Colorama
        init(convert=True)
    def __LogError(self, string):
        try:
            print(bcolors.WARNING + "[!] " + bcolors.ENDC + "Error: " + string)
        except Exception:
            print("Error: " + string)

    def __LogInfo(self, string):
        try:
            print(bcolors.OKGREEN + "[+] " + bcolors.ENDC + string)
        except Exception:
            print("Error: " + string)

    def __Request(self, query, header, type: HTTPMethod, data="") -> bool:
        try:
            if type == HTTPMethod.GET:
                self.r = requests.get(query, headers=header)
            if type == HTTPMethod.PUT:
                self.r = requests.put(query, headers=header, data=data)
            if type == HTTPMethod.POST:
                self.r = requests.post(query, headers=header, data=data)
            if type == HTTPMethod.NOREDIRECT:
                self.r = requests.get(query, allow_redirects=False)
        except HTTPError as e:
            self.__LogError(f"HTTP: {e}")
            return False
        except Exception as e:
            self.__LogError(f"Exception: {e}")
            return False

        if self.r.status_code == StatusCode.TooManyRequests:
            self.__LogError("Too many requests done. Either wait a few minutes or check with QueriesLeft function!")
            return False

        isError = False
        for code in ErrorStatusCode:
            # Most likely if something bad happened with the get request.
            if self.r.status_code == code:
                isError = True
        if isError:
            self.__LogError(f"Query returned a bad status code: {self.r.status_code}.")
            try:
                self.__LogError(f"Message {self.r.json()['error']['message']}")
            except Exception:
                print(self.r.text)
            except TypeError:
                print(self.r.text)
            return False
        else:
            self.__LogInfo(f"Query complete with status code: {self.r.status_code}")
           

        return True

    def GetToken(self):
        from dotenv import dotenv_values
        # Needed to get token
        config = dotenv_values(".env")
        scopes = urllib.parse.quote("playlist-modify-public playlist-modify-private playlist-read-private ugc-image-upload")
        redirect_uri = urllib.parse.quote("http://127.0.0.1:5273")
        url = 'https://accounts.spotify.com/authorize?response_type=code&client_id=' + config['SPOTIFY_CLIENT_ID'] + '&redirect_uri=' + redirect_uri + "&scope=" + scopes
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            self.__LogError("Unable to open standard browser, please open the url in your preferred browser: " + url)
            pass
        import GetHandler
        self.__LogInfo("Awaiting token, please login!")
        access_token = GetHandler.run()
        self.__LogInfo("Successfully acquired access token! Asking spotify for auth code")

        body = {'grant_type': 'authorization_code', 'code': f'{access_token}', 'redirect_uri': 'http://127.0.0.1:5273'}
        
        client_id = config['SPOTIFY_CLIENT_ID']
        client_secret = config['SPOTIFY_CLIENT_SECRET']
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())

        header = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': f'Basic {client_creds_b64.decode()}'}

        if self.__Request("https://accounts.spotify.com/api/token", header, HTTPMethod.POST, body) == False:
            return

        
        self.token = json.loads(self.r.text)['access_token']
        self.tokenIsSet = True


    def GetPlaylist(self) -> dict:
        #[TODO]: This only returns two, i think?
        if self.tokenIsSet == False:
            self.__LogError("Token has not been set.")
            return

        self.__LogInfo("Querying Spotify for Playlist")
        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        
        if self.__Request("https://api.spotify.com/v1/me/playlists", header, HTTPMethod.GET) == False:
            return

        data = json.loads(self.r.text)
        namesList = {}
        # Get the users id, this is what we use to check wether you own the playlist or not.
        user = data['href']
        foo = user.split('/')
        fooUsers = 0

        if 'users' in foo:
            fooUsers = list(foo).index('users')

        userIdLoc = fooUsers + 1

        userId = foo[userIdLoc]

        # Get owned playlists
        for items in data['items']:
            playlistOwnerId = items['owner'].get('uri')
            bar = playlistOwnerId.split(':')
            if bar[2] == userId:
                baz = items.get('uri').split(':')[2]
                # Name of playlist and playlist id
                namesList[items['name']] = baz


        # Print owned playlists
        for k, v in namesList.items():
            print(f"\nOwned Playlist Name: {k}\nOwned Playlist Id: {v}\n")
        
        # Returns list, can always be used by someone.
        return namesList
    
    def __SendShuffle(self, tracks, newPlaylistID):
        # Shuffle array with song id
        self.__LogInfo(f"Shuffling a total of {len(tracks)} songs!")

        # Shuffle 20 timse
        import sys
        sys.stdout.write(bcolors.OKGREEN + "[+] " + bcolors.ENDC + "Shuffling: ")
        progress = "#"
        j = 0
        for i in range(0, 19):
            random.shuffle(tracks)
            if i % 4 == 0:
                sys.stdout.write(progress)
                sys.stdout.flush()
                progress += "#"
        print("")

        trackStr = ','.join(tracks)

        self.__LogInfo("Sending shuffled songs to new playlist")

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        
        return self.__Request(f"https://api.spotify.com/v1/playlists/{newPlaylistID}/tracks?uris={trackStr}", header, HTTPMethod.POST)

    def Shuffle(self, playlistId: str):
        if self.tokenIsSet == False:
            self.__LogError("Token has not been set.")
            return

        # Query spotify to get information about the playlist
        self.__LogInfo("Querying Spotify to get information about chosen playlist")
        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        if self.__Request(f"https://api.spotify.com/v1/playlists/{playlistId}", header, HTTPMethod.GET) == False:
            return

        data = json.loads(self.r.text)
        
        # Cover image
        cover = ""
        for images in data['images']:
            if images.get('height') == 640:
                cover = images.get('url')
                break

        
        # User Id
        userID = data['owner']['uri']
        userID = userID.split(':')[2]

        name = data['name']
        description = data['description']
        public = data['public']

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        
        # Construct a new playlist.
        self.__LogInfo("Creating Playlist")

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        
        _data = {'name' : f'{name} (Shuffled)', 'description' : description, 'public' : public}
        # This is needed to convert the python bool to a json bool!
        data = json.dumps(_data)

        if self.__Request(f"https://api.spotify.com/v1/users/{userID}/playlists", header, HTTPMethod.POST, data) == False:
            return

        # Query returns the id of the recently made playlist, grab it.
        _foo = json.loads(self.r.text)
        newPlaylistID = _foo['id']

        self.__LogInfo(f"New playlist created with ID: {newPlaylistID}")

        # Query spotify for the actual songs in playlist
        self.__LogInfo("Querying Spotify about tracks in the playlist")

        if self.__Request(f"https://api.spotify.com/v1/playlists/{playlistId}/tracks", header, HTTPMethod.GET) == False:
            return
        
        data = json.loads(self.r.text)
        
        needed_queries = math.ceil(data['total'] / 100)
        offset = 0

        tracks = []
        for i in range(0, needed_queries):

            for items in data['items']:
                tracks.append(items['track'].get('uri'))

            if self.__SendShuffle(tracks, newPlaylistID) == True:
                
                header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
                offset += 1
                if self.__Request(f"https://api.spotify.com/v1/playlists/{playlistId}/tracks?offset={offset * 100}", header, HTTPMethod.GET) == False:
                    return False
                tracks.clear()
                data = json.loads(self.r.text)

        self.__LogInfo("Uploading Cover Image")

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}

        # Download original cover and encode to base64.
        _cover = base64.b64encode(requests.get(cover, allow_redirects=True).content)


        return self.__Request(f"https://api.spotify.com/v1/playlists/{newPlaylistID}/images", header, HTTPMethod.PUT, _cover)

    def GetUser(self):
        self.__LogInfo("This does nothing!")

    def QueriesLeft(self):
        if self.tokenIsSet == False:
            self.__LogError("Token has not been set.")
            return

        # TODO: Actually print out the rate limit, however i have no idea how that looks like.
        print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Querying spotify")
        self.r = requests.get("https://api.spotify.com/v1/me")
        self.__LogInfo("This function, for now does not tell in a good way when the rate limit is done. Report back to the creator on how a header with rate limit looks like and it can get implemented.\n")
        print(self.r.headers)



if __name__ == "__main__":
    import sys
    sys.stdout.buffer.write(b" ____  _            __  __ _           \n")
    sys.stdout.buffer.write(b"/ ___|| |__  _   _ / _|/ _| | ___ _ __ \n")
    sys.stdout.buffer.write(b"\___ \| '_ \| | | | |_| |_| |/ _ \ '__|\n")
    sys.stdout.buffer.write(b" ___) | | | | |_| |  _|  _| |  __/ |   \n")
    sys.stdout.buffer.write(b"|____/|_| |_|\__,_|_| |_| |_|\___|_|   \n\n")
    sys.stdout.write("Usage: Shuffle 'playlist id' 'token'.\nHelp: help\n")

    # TODO: Make this better in some way
    ss = SpotifyShuffler()
    while(True):
        playlists = {}
        arg = ""
        foo = input("Shell: ")
        read = foo.split(" ")[0]
        if read.lower() == 'exit':
            sys.stdout.write("Quitting...\n")
            break
        elif read.lower() == 'help':
            sys.stdout.write("SpotifyShuffler uses a shell like way of entering commands.\n\nGetToken -- ***Opens in your browser*** You are required to login with your spotify, this gives you a token which we can then use.\n\nGetPlaylist -- returns playlist the user owns, or can be shuffled.\n\nShuffle playlistID -- Shuffles the specified playlist, NOTE: Shuffled version will be in a new playlist.\n\nQueriesLeft -- If error code is '429' that means you are rate limited, check cooldown.\n\nStatusCode -- prints what every status code means\n")
        elif read.lower() == 'gettoken':
            ss.GetToken()
        elif read.lower() == 'getplaylist':
            ss.GetPlaylist()
        elif read.lower() == 'shuffle':
            # This too
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.Shuffle(arg)
        elif read.lower() == 'queriesleft':
            ss.QueriesLeft()
        elif read.lower() == 'statuscode':
            sys.stdout.write("Status Codes: Ok = 200\nCreated = 201\nAccepted = 202\nNoContent = 204\nNotModified = 304\nBadRequest = 400\nUnauthorized = 401\nForbidden = 403\nNotFound = 404\nTooManyRequests = 429\nInternalServerError = 500\nBadGateway = 502\nServiceUnavailable = 503\n") 
        else:
            sys.stdout.write("Unknown command, try again.\n")
