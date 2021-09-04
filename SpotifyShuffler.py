from enum import IntEnum
import requests
from colorama import init

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
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SpotifyShuffler:
    token = None
    def __init__(self, token):
        # Colorama
        init(convert=True)
        self.token = token

    def GetPlaylist(self):
        print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Querying Spotify")
        header = {'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : 'Bearer %s' % self.token}
                
        
        self.r = requests.get("https://api.spotify.com/v1/me/playlists", headers=header)

        if self.r.status_code == StatusCode.TooManyRequests:
            print(f"{bcolors.WARNING}[!]{bcolors.ENDC} Error: Too many requests done. Either wait a few minutes or check with QueriesLeft function!")

        isError = False
        for code in ErrorStatusCode:
            # Most likely if something bad happened with the get request.
            if self.r.status_code == code:
                isError = True
        if isError:
            print(f"{bcolors.WARNING}[!]{bcolors.ENDC} Error: Query returned a bad status code: {self.r.status_code}.")
        else:
            print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Query complete with status code: {self.r.status_code}")

        print(f"[+]")

    def GetUser(self, token):
        print("asd")

    def QueriesLeft(self, token):
        # TODO: Actually print out the rate limit, however i have no idea how that looks like.
        print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Querying spotify")
        self.r = requests.get("https://api.spotify.com/v1/me")
        print("This function, for now does not tell in a good way when the rate limit is done. Report back to the creator on how a header with rate limit looks like and it can get implemented.\n")
        print(self.r.headers)

        



if __name__ == "__main__":
    # Just a quick fix.
    # TODO: Make this work
    import sys
    ss = SpotifyShuffler(sys.argv[1])