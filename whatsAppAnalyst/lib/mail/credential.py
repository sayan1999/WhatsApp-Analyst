from cryptography.fernet import Fernet
import json

def getCred(keyfile):

    file = open(keyfile, 'rb')
    key = file.read()
    file.close()

    f = Fernet(key)
    encrypted = b'gAAAAABejoBBiwTw9QDbYyLlfrBiG_w93vQpr597hLyIFP-Y11d-gmwL9svpKQx-vsWP1PMFwR2CXMi0iec5bvvoKPa6Axr9GD1Z2jpzEAv3fPvxFXZ5JQ3scXVInFGX0Q4-84vZwYaWCtHLTURGG0_b_MM-vpHrkvmALAAr6BjSrUFpXfTAd5s='
    decrypted = f.decrypt(encrypted)
    obj = json.loads(decrypted.decode('utf-8'))
    return obj['USER'], obj['PASSWORD']