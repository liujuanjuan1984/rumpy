import os

PORT = 62663
CRTFILE = r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum-bin\certs\server.crt"
if not os.path.exists(CRTFILE):
    try:
        import certifi

        CRTFILE = certifi.where()
    except:
        CRTFILE = True

CLIENT_PARAMS = {"port": PORT, "crtfile": CRTFILE}
