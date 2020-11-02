import random
STATION_IDENTS = [7, 8, 9, 13, 16, 17, 19, 20, 23, 24, 26, 27, 29, 31, 33, 35]
RNH_ADS = [14998, 14999]


def findStationIdent():
    return random.choice(STATION_IDENTS)


def findRNHAd():
    return random.choice(RNH_ADS)
