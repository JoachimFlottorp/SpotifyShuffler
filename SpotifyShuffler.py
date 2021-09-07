from enum import IntEnum
import requests
from requests.exceptions import HTTPError
from colorama import init
import json
import random
import base64
import webbrowser
import urllib.parse

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
        print(bcolors.WARNING + "[!] " + bcolors.ENDC + "Error: " + string)

    def __LogInfo(self, string):
        print(bcolors.OKGREEN + "[+] " + bcolors.ENDC + string)

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
            self.__LogError(f"{e}")
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
            self.__LogError(f"Message {self.r.json()['error']['message']}")
            return False
        else:
            self.__LogInfo(f"Query complete with status code: {self.r.status_code}")

        return True

    def GetToken(self):
        from dotenv import dotenv_values
        config = dotenv_values(".env")
        scopes = urllib.parse.quote_plus("playlist-read-private ugc-image-upload playlist-modify-public playlist-modify-private playlist-read-public playlist-read-private")
        redirect_uri = urllib.parse.quote_plus("https://google.com/")
        url = 'https://accounts.spotify.com/authorize?response_type=code&client_id=' + config['SPOTIFY_CLIENT_ID'] + '&redirect_uri=' + redirect_uri + "&scope=" + scopes
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            print("Unable to open browser, url: " + url)
            pass

    def GetPlaylist(self, token="") -> dict:
        if self.tokenIsSet == False:
            if token != "":
                self.token = token
                self.tokenIsSet = True
            else:
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
    
    def Shuffle(self, playlistId: str, token=""):
        if self.tokenIsSet == False:
            if token != "":
                self.tokenIsSet = True
                self.token = token
            else:
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
            cover = images.get('url')
        
        # User Id
        userID = data['owner']['uri']
        userID = userID.split(':')[2]

        name = data['name']
        description = data['description']
        public = data['public']

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
        
        # Query spotify for the actual songs in playlist
        self.__LogInfo("Querying Spotify about tracks in the playlist")

        if self.__Request(f"https://api.spotify.com/v1/playlists/{playlistId}/tracks", header, HTTPMethod.GET) == False:
            return
        
        data = json.loads(self.r.text)

        tracks = []
            
        for items in data['items']:
            tracks.append(items['track'].get('uri'))

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
        
        if self.__Request(f"https://api.spotify.com/v1/playlists/{newPlaylistID}/tracks?uris={trackStr}", header, HTTPMethod.POST, ) == False:
            return

        self.__LogInfo("Uploading Cover Image")

        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}

        # Download original cover and encode to base64.
        _cover = base64.b64encode(requests.get(cover, allow_redirects=True).content)


        if self.__Request(f"https://api.spotify.com/v1/playlists/{newPlaylistID}/images", header, HTTPMethod.PUT, _cover) == False:
            return
        
        
        # https://stackoverflow.com/questions/52907414/python-web-scrape-dealing-with-user-login-popup

    def GetUser(self, token):
        self.__LogInfo("This does nothing!")

    def QueriesLeft(self, token=''):
        if self.tokenIsSet == False:
            if token != "":
                self.tokenIsSet = True
                self.token = token
            else:
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
            sys.stdout.write("SpotifyShuffler uses a shell like way of entering commands.\n\nGetToken -- ***Opens in your browser*** You are required to login with your spotify, this gives you a token which we can then use.\n\nGetPlaylist token(If not set)-- returns playlist the user owns, or can be shuffled.\n\nShuffle playlistID token(If not set) -- Shuffles the specified playlist, NOTE: Shuffled version will be in a new playlist.\n\nQueriesLeft -- If error code is '429' that means you are rate limited, check cooldown.\n\nStatusCode -- prints what every status code means\n")
        elif read.lower() == 'gettoken':
            # Make this more functional or something..
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.GetToken()
        elif read.lower() == 'settokenownapp':
            ss.SetTokenOwnApp()
        elif read.lower() == 'getplaylist':
            # This too
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.GetPlaylist(arg)
        elif read.lower() == 'queriesleft':
            # This too
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.QueriesLeft(arg)
        elif read.lower() == 'statuscode':
            sys.stdout.write("Status Codes: Ok = 200\nCreated = 201\nAccepted = 202\nNoContent = 204\nNotModified = 304\nBadRequest = 400\nUnauthorized = 401\nForbidden = 403\nNotFound = 404\nTooManyRequests = 429\nInternalServerError = 500\nBadGateway = 502\nServiceUnavailable = 503\n") 
        else:
            sys.stdout.write("Unknown command, try again.\n")
