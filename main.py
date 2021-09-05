from SpotifyShuffler import *

if __name__ == "__main__":
    token = "BQDZ9LXhHteDp7mEGsNCaIjzgizs816rJTZ18JHsZfY2sFpqkDQ5zDPlyQ5PdivM2W8pb41UFg0eIBn5BapWDMQepmLE6NC73sYCGo66rh1sBH0ikk8ge2scyYJzKbGgmpgW5twR3_uCY5h9AwLdzZ5V6lCCebLqx3r3Dy2Y2RT92ztF74LkkBKPYbRNeQ"
    ss = SpotifyShuffler(token)
    # ss.GetUser(token)
    # ss.QueriesLeft(token)
    ss.GetPlaylist()
