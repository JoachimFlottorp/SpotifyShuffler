from enum import IntEnum
import requests
from requests.exceptions import HTTPError
from colorama import init
import json

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
                self.r = requests.put(query, headers=header)
            if type == HTTPMethod.POST:
                self.r = requests.post(query, headers=header, data=data)
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

    def SetToken(self, string):
        self.token = string
        self.tokenIsSet = True
        self.__LogInfo("Token set!")

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

        print(data)
        if self.__Request(f"https://api.spotify.com/v1/users/{userID}/playlists", header, HTTPMethod.POST, data) == False:
            return





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
    sys.stdout.write("Usage: Shuffle 'token' 'playlist id'.\nHelp: help\n")

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
            sys.stdout.write("SpotifyShuffler uses a shell like way of entering commands.\n\nSetToken token -- sets the token for other commands.\n\nGetPlaylist token(If not set)-- returns playlist the user owns, or can be shuffled.\n\nShuffle playlist-id token(If not set) -- Shuffles the specified playlist, NOTE: Shuffled version will be in a new playlist.\n\nQueriesLeft -- If error code is '429' that means you are rate limited, check cooldown.\n\nStatusCode -- prints what every status code means\n")
        elif read.lower() == 'settoken':
            # Make this more functional or something..
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.SetToken(arg)
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
