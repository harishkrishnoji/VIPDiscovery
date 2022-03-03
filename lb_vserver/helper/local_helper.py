# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
import json
import requests
from helper_fts.logger import get_logger
from helper.gitlab_helper import GitLab_Client
# from helper_fts.vault import hashi_vault_rundeck

from helper_fts.vault import hashi_vault


requests.packages.urllib3.disable_warnings()

log = get_logger()
token = os.environ.get("HASHI_TOKEN")
glab = GitLab_Client()

vdata = {
    "namespace": os.environ.get("VAULT_NAMESPACE"),
    "role_id": os.environ.get("VAULT_ROLE_ID"),
    "secret_id": os.environ.get("VAULT_SECRET_ID"),
}


def uploadfile(sas_vip_info, env):
    """Update VIP data on to remote server and Nautobot."""
    filename = f"{env}.json"
    with open(filename, "w+") as json_file:
        json.dump(sas_vip_info, json_file, indent=4, separators=(",", ": "), sort_keys=True)
    resp = _uploadfile(filename)
    gitUpload(filename, env)
    return resp.strip()


def gitUpload(filename, env):
    glab.filepath = f"lb-vip/{env}.json"
    glab.update_file(filename)


def _uploadfile(fname):
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


def get_credentials():
    path = "loadbalancer_secrets"
    vault_data = hashi_vault(token=token, path=path)
    # vdata["path"] = path
    # vault_data = hashi_vault_rundeck(**vdata)
    svcp = vault_data["data"]["data"]["svc_acc"].get("password")
    svcu = vault_data["data"]["data"]["svc_acc"].get("username")
    lowu = vault_data["data"]["data"]["f5_lower"].get("username")
    lowp = vault_data["data"]["data"]["f5_lower"].get("password")
    return svcp, svcu, lowu, lowp


def get_nb_keys(nburl):
    path = "nautobot"
    vault_data = hashi_vault(token=token, path=path)
    # vdata["path"] = path
    # vault_data = hashi_vault_rundeck(**vdata)
    if "-cat" in nburl.lower():
        return vault_data["data"]["data"]["keys"].get("cat")
    return vault_data["data"]["data"]["keys"].get("prod")


def get_git_keys():
    path = "gitlab"
    vault_data = hashi_vault(token=token, path=path)
    # vdata["path"] = path
    # vault_data = hashi_vault_rundeck(**vdata)
    return vault_data["data"]["data"].get("fts_sane_wr")
