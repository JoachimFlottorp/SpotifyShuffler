from SpotifyShuffler import *

if __name__ == "__main__":
    token = "BQAFPpnzEvRByvlY_Lx_tGztthT4Iqxw0nCf7vdvhPtnd507KAlYbPB7OyTYa1ITFmg8JPjxarL8HFemc20QicjQMZ4p0IsDufRSFsFX5SLQJAWLAFpWFJPpZ67R8RRsHhjzvD49DbY0WKL9WJCodhE7wf8c-Trhxj9DrD9PvBXtBe-OaL3ql4EF-0P7qQ"
    ss = SpotifyShuffler()
    # ss.GetUser(token)
    # ss.QueriesLeft(token)
    ss.SetToken(token)
    # ss.GetPlaylist()
    # 4uTVnVrmsuarBVHeriLKm8
    ss.Shuffle("4uTVnVrmsuarBVHeriLKm8")
