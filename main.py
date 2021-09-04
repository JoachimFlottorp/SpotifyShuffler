from SpotifyShuffler import *

if __name__ == "__main__":
    token = "asd"
    # token = "BQCgrbRztr9fjapVusWVLf1X6F2eCwPm78xnhzLqceMosACqbu34M5umS5VPbmxDzFCQRPR2K8jFgCBP88tt_JOGwSKl-4LgZNAaIg5qdhWOkdls7oWruk6lxFlj_A5K55wgqBXLLe-lIPC3qiUGcxFLJbqOCqocwfhTzlE3t13FMLEpQY4"
    ss = SpotifyShuffler(token)
    ss.GetUser(token)
    # ss.QueriesLeft(token)
    # ss.GetPlaylist()