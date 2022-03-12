# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
import json
import requests
from deepdiff import DeepDiff
from nautobot.nautobot_main import NautobotClient
from helper import log, deviceToQuery, env, glab, gitFile, edata
from helper_fts.email import send_email


requests.packages.urllib3.disable_warnings()


def uploadFile(sas_vip_info):
    """Update VIP data on to remote server and GitLab."""
    if "All" in deviceToQuery:
        filename = f"{env}.json"
        with open(filename, "w+") as json_file:
            json.dump(sas_vip_info, json_file, indent=4, separators=(",", ": "), sort_keys=True)
        _uploadFileSAS(filename)
        _uploadFileGIT(filename)


def _uploadFileGIT(fname):
    """Upload file to GITLab Repo."""
    glab.filepath = f"lb-vip/{env}.json"
    glab.update_file(fname)


def _uploadFileSAS(fname):
    """Upload file to remote server."""
    url = "https://uschd1linjmp01a.1dc.com/cgi-bin/uploadfile.py"
    files = [("filename", (os.path.basename(fname), open(fname, "rb")))]
    response = requests.request("POST", url, files=files, verify=False)
    log.info(response.text.strip())


def getFileSAS(fname=""):
    """Get file from remote server."""
    url = f"https://uschd1linjmp01a.1dc.com/NAT/{fname}"
    response = requests.request("GET", url, verify=False)
    if response.status_code == 200:
        return json.loads(response.text)


def nautobotUpdate(device):
    """Update Nautobot."""
    ovips = len(device.get("vips", []))
    if gitFile:
        device = diffObject(device)
    log.info(f"{device.get('hostname')}: [{ovips}] Total VIPs, [{len(device.get('vips', []))}] VIPs to update Nautobot")
    edata.append(
        f"{device.get('hostname')}: [{ovips}] Total VIPs, [{len(device.get('vips', []))}] VIPs to update Nautobot"
    )
    if device.get("vips"):
        NautobotClient(device)


def diffObject(device):
    """Run DeepDiff."""
    nvips = device.get("vips")
    newdev = device.copy()
    newdev["vips"] = []
    for nd in nvips:
        newvip = True
        for od in gitFile:
            if objFilter(od, nd) and not objDeepDiff(od, nd):
                newvip = False
        if newvip:
            newdev["vips"].append(nd)
    return newdev


def objFilter(od, nd):
    """Diff filter."""
    if (
        (od.get("port") == nd.get("port"))
        and od.get("protocol") == nd.get("protocol")
        and (od.get("address") == nd.get("address"))
        and (od.get("name") == nd.get("name"))
        and (od.get("pool") == nd.get("pool"))
        and (od.get("environment") == nd.get("environment"))
    ):
        return True


def objDeepDiff(od, nd):
    """Diff filter Pool Members."""
    if od.get("pool_mem") and "1.1.1.1" in od.get("pool_mem"):
        return DeepDiff(
            od,
            nd,
            ignore_order=True,
            exclude_paths=["root['loadbalancer']", "root['loadbalancer_address']", "root['pool_mem']"],
        )
    return DeepDiff(od, nd, ignore_order=True, exclude_paths=["root['loadbalancer']", "root['loadbalancer_address']"])


def VIPEmail():
    """Email."""
    msg = {}
    msg["to"] = "SANE-ContentSolutions@fiserv.com, Ashok.Ramaswamy@Fiserv.com, Shashikant.Patel@Fiserv.com, bhavdeep.singh@Fiserv.com"
    msg["cc"] = "harish.krishnoji@fiserv.com"
    msg["body"] = edata
    send_email(**msg)
