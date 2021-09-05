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

    def SetToken(self, string):
        self.token = string
        self.tokenIsSet = True

    def GetPlaylist(self, token="") -> dict:
        if self.tokenIsSet == False:
            if token != "":
                self.tokenIsSet = True
                self.token = token
            else:
                self.__LogError("Token has not been set.")
                return
        

        self.__LogInfo("Querying Spotify")
        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
                
        try:
            self.r = requests.get("https://api.spotify.com/v1/me/playlists", headers=header)
        except HTTPError as e:
            self.__LogError(f"HTTP: {e}")
        except Exception as e:
            self.__LogError(f"{e}")

        if self.r.status_code == StatusCode.TooManyRequests:
            self.__LogError("Too many requests done. Either wait a few minutes or check with QueriesLeft function!")
            return

        isError = False
        for code in ErrorStatusCode:
            # Most likely if something bad happened with the get request.
            if self.r.status_code == code:
                isError = True
        if isError:
            self.__LogError(f"Query returned a bad status code: {self.r.status_code}.")
            return
        else:
            self.__LogInfo(f"Query complete with status code: {self.r.status_code}")

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
        print(userId)

        for items in data['items']:
            playlistOwnerId = items['owner'].get('uri')
            bar = playlistOwnerId.split(':')
            if bar[2] == userId:
                namesList[items['name']] = bar[2]


        print(namesList)
        return namesList
                

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

    # TODO: How does bash in linux do this, make it work like that?
    while(True):
        playlists = {}
        arg = ""
        ss = SpotifyShuffler()
        foo = input("Shell: ")
        read = foo.split(" ")[0]
        if read.lower() == 'exit':
            sys.stdout.write("Quitting...\n")
            break
        elif read.lower() == 'help':
            sys.stdout.write("SpotifyShuffler uses a shell like way of entering commands.\n\nSetToken token -- sets the token for other commands.\n\nGetPlaylist token(If not set)-- returns playlist the user owns, or can be shuffled.\n\nShuffle playlist-id token(If not set) -- Shuffles the specified playlist\nQueriesLeft -- If error code is '429' that means you are rate limited, check cooldown.\n")
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
            playlists = ss.GetPlaylist(arg)
        elif read.lower() == 'queriesleft':
            # This too
            try:
                arg = foo.split(" ")[1]
            except (ValueError, IndexError):
                pass
            ss.QueriesLeft(arg) 
        else:
            sys.stdout.write("Unknown command, try again.\n")
        
    # ss = SpotifyShuffler(sys.argv[1])
    # userOwnedPlaylists = ss.GetPlaylist()