from hashlib import md5

def fingerprint(ip_address, target, user_agent):
    return md5((ip_address+target+user_agent).encode('utf-8')).hexdigest()
