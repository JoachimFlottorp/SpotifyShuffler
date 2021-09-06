from SpotifyShuffler import *

if __name__ == "__main__":
    token = "BQAjfL3qCLyVgWfCDQ8N_vahqGAbuDT7AkSkM3rfsp4UkRhbZIKyrPgwcMDsFTkrm4PtozD9hrmH5XPbDDB5I7oEv0HbRbN2YRjjhbj7axVCKMYv7jZtGLkjw5mGwfB7LxepagGTqO7Ot9oLAd1wTKnnBwFO64zIoFR7v7NpJevXnIx4Q0KuLQ3lEkQ0Wh8Mw0FKFtX39ZJcrBgu35LmcCx26M_quLpGSkJymNpWsdppY6r9gd8PrQ-6"
    ss = SpotifyShuffler()
    # ss.GetUser(token)
    # ss.QueriesLeft(token)
    ss.SetToken(token)
    # ss.GetPlaylist()
    # 4uTVnVrmsuarBVHeriLKm8
    ss.Shuffle("4uTVnVrmsuarBVHeriLKm8")
