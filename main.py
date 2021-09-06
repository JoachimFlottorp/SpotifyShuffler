from SpotifyShuffler import *

if __name__ == "__main__":
    token = "BQB-dCMM2KZIEgWzXUd9x_7LDesZyLn-RQnDnITFMw2_Y9ezfNCJB4YdpEREWLeNst69wcoJ3Uc-OneO72pi1how8WfQPDvgwdt-v6wWZ90wXXFHcrSYCIJYei3lkc7VdGvPSCBmk04OLxNZElnsPTz48BTPV1-GH5cM2gMwoQ75GMhNLqR_RP29IxB50W1DO8ttdmtqc4Jsii46kcAUYgPq5grzBo_YOVs"
    ss = SpotifyShuffler()
    # ss.GetUser(token)
    # ss.QueriesLeft(token)
    ss.SetToken(token)
    # ss.GetPlaylist()
    # 4uTVnVrmsuarBVHeriLKm8
    ss.Shuffle("4uTVnVrmsuarBVHeriLKm8")
