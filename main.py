from SpotifyShuffler import *

if __name__ == "__main__":
    token = "BQBDVezJCJHr7DmQVmbfWIt9i2QHmVnzYPzBuztgD0SCYaWliPo2dBAm_QsCBQKYraroAn1toav3MdXoZAmLckgQnHMDmF1d0pQ6XlM_1m-p2w-rTRmnJQWSj0npGUUaoS2Sos35LnnwqGKU0DsOv9vGH3fRsD57hkwaBTC72AsJ9y90sUfUg4GTPVvlwQf9i9xX3t2S3-SnYSc8GWXQvCVWVDDwSkxP"
    ss = SpotifyShuffler()
    # ss.GetUser(token)
    # ss.QueriesLeft(token)
    ss.SetToken(token)
    # ss.GetPlaylist()
    # 4uTVnVrmsuarBVHeriLKm8
    ss.Shuffle("4uTVnVrmsuarBVHeriLKm8")
