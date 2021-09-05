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
    def __init__(self, token):
        # Colorama
        init(convert=True)
        self.token = token

    def __LogError(self, string):
        print(bcolors.WARNING + "[!]" + bcolors.ENDC + "Error: " + string)

    def __LogInfo(self, string):
        print(bcolors.OKGREEN + "[+] " + bcolors.ENDC + string)

    def GetPlaylist(self):
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
                namesList[items['name']] = bar


        print(namesList)
                

    def GetUser(self, token):
        self.__LogInfo("This does nothing!")

    def QueriesLeft(self, token):
        # TODO: Actually print out the rate limit, however i have no idea how that looks like.
        print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Querying spotify")
        self.r = requests.get("https://api.spotify.com/v1/me")
        self.__LogInfo("This function, for now does not tell in a good way when the rate limit is done. Report back to the creator on how a header with rate limit looks like and it can get implemented.\n")
        print(self.r.headers)



if __name__ == "__main__":
    # Just a quick fix.
    # TODO: Make this work
    import sys
    ss = SpotifyShuffler(sys.argv[1])
    ss.GetPlaylist()