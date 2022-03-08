# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
import json
import requests
from helper_fts.logger import get_logger
from helper.gitlab_helper import GitLab_Client
from nautobot.nautobot_main import NautobotClient
from deepdiff import DeepDiff


# from helper_fts.vault import hashi_vault_rundeck

from helper_fts.vault import hashi_vault


requests.packages.urllib3.disable_warnings()

log = get_logger()
token = os.environ.get("HASHI_TOKEN")
env = os.environ.get("RD_OPTION_ENV")


vdata = {
    "namespace": os.environ.get("VAULT_NAMESPACE"),
    "role_id": os.environ.get("VAULT_ROLE_ID"),
    "secret_id": os.environ.get("VAULT_SECRET_ID"),
}


def get_git_keys():
    path = "gitlab"
    vault_data = hashi_vault(token=token, path=path)
    # vdata["path"] = path
    # vault_data = hashi_vault_rundeck(**vdata)
    return vault_data["data"]["data"]["access_token"].get("sane_backups")


git_token = get_git_keys()
glab = GitLab_Client(token=git_token, filepath=f"lb-vip/{env}.json")
gfile = json.loads(glab.get_file().decode()) if glab.get_file() else ""


def uploadfile(sas_vip_info, env):
    """Update VIP data on to remote server and GitLab."""
    if os.environ.get("RD_OPTION_DEVICES") == "All":
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


def update_nautobot(device):
    if gfile:
        device = diffObject(device)
    NautobotClient(device)


def diffObject(device):
    nvips = device.get("vips")
    newdev = device.copy()
    newdev["vips"] = []
    log.info(f"New VIPs count : {len(nvips)}")
    log.info(f"Old VIPs count : {len(gfile)}")
    for nd in nvips:
        newvip = True
        for od in gfile:
            if (
                (od.get("port") == nd.get("port"))
                and od.get("protocol") == nd.get("protocol")
                and (od.get("address") == nd.get("address"))
                and (od.get("name") == nd.get("name"))
                and (od.get("pool") == nd.get("pool"))
                and (od.get("environment") == nd.get("environment"))
            ):
                if not DeepDiff(od, nd, ignore_order=True, exclude_paths=["root['loadbalancer']"]):
                    newvip = False
        if newvip:
            newdev["vips"].append(nd)
    log.info(f"After filter VIPs count : {len(newdev['vips'])}")
    return newdev
