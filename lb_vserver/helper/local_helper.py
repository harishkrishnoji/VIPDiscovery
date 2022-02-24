# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
import json
import requests
from helper_fts.logger import get_logger
from helper_fts.vault import hashi_vault

requests.packages.urllib3.disable_warnings()

log = get_logger()


def uploadfile(fname):
    """Upload file to remote server.

    Args:
        fname (str): Filename which need to be uploaded
    """
    url = "https://uschd1linjmp01a.1dc.com/cgi-bin/uploadfile.py"
    files = [("filename", (os.path.basename(fname), open(fname, "rb")))]
    response = requests.request("POST", url, files=files, verify=False)
    return response.text


def getfile(fname=""):
    """Get file from remote server."""
    url = f"https://uschd1linjmp01a.1dc.com/NAT/{fname}"
    response = requests.request("GET", url, verify=False)
    if response.status_code == 200:
        return json.loads(response.text)


def get_credentials(token, path):
    path = "loadbalancer_secrets"
    vault_data = hashi_vault(token=token, path=path)
    svcp = vault_data["data"]["data"]["svc_acc"].get("password")
    svcu = vault_data["data"]["data"]["svc_acc"].get("username")
    lowu = vault_data["data"]["data"]["f5_lower"].get("username")
    lowp = vault_data["data"]["data"]["f5_lower"].get("username")
    return svcp, svcu, lowu, lowp


def get_nb_keys(token, path):
    path = "nautobot"
    vault_data = hashi_vault(token=token, path=path)
    key = vault_data["data"]["data"]["keys"].get("cat")
    # key = vault_data["data"]["data"]["keys"].get("prod")
    return key
