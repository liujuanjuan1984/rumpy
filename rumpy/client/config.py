# quorum config info
import os
import certifi

PORT = 58356
CRTFILE = r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt"
if not os.path.exists(CRTFILE):
    try:
        CRTFILE = certifi.where()  #
    except:
        CRTFILE = True
# C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum-bin\certs
CLIENT_PARAMS = {"port": PORT, "crtfile": CRTFILE}
