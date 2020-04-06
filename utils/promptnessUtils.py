BONUS={
    0 : 1,
    1 : 2,
    2 : 2.5,
    3 : 4,
    4 : 5,
    5 : 6
}

MSGPTS = {
    0 : 0.0,
    1 : 0.3333333333333333,
    2 : 0.6666666666666666,
    3 : 1.0,
    4 : 1.3333333333333333,
    5 : 1.6666666666666667,
    6 : 2.0,
    7 : 2.3333333333333335,
    8 : 2.6666666666666665,
    9 : 3.0,
    10 : 3.3333333333333335,
    11 : 3.6666666666666665,
    12 : 4.0,
    13 : 4.333333333333333,
    14 : 4.666666666666667,
    15 : 5.0,
    16 : 5.333333333333333,
    17 : 5.666666666666667,
    18 : 6.0,
    19 : 6.333333333333333,
    20 : 6.666666666666667,
    21 : 7.0,
    22 : 7.333333333333333,
    23 : 7.666666666666667,
    24 : 8.0,
    25 : 8.333333333333334,
    26 : 8.666666666666666,
    27 : 9.0,
    28 : 9.333333333333334,
    29 : 9.666666666666666 
}
MAXBONUS=50
MAXPENALTY=200
SPAMMESSAGELENGTH=200

def getbonusForRec(recurrency):

    return min(1.5 ** (1+recurrency), MAXBONUS)

def getlen(message):

    if len(message) >= SPAMMESSAGELENGTH:
        return 3
    return len(message)


def pointsForMsg(length):
        
    return MSGPTS.get(length, 10)/3

def getPnltyForRec(recurrency):

    return min(2 ** (1+recurrency), MAXPENALTY)

def penaltyForDelay(conversation, delay, recurrency):

    if conversation:
        return delay

    else:
        return getPnltyForRec(recurrency)