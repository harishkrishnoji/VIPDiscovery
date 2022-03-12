# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
from helper_fts.vault import hashi_vault_rundeck

nburl = os.environ.get("RD_OPTION_NAUTOBOT_URL")
vdata = {
    "namespace": os.environ.get("VAULT_NAMESPACE"),
    "role_id": os.environ.get("VAULT_ROLE_ID"),
    "secret_id": os.environ.get("VAULT_SECRET_ID"),
}


def getGITtoken():
    """Get GIT token."""
    vdata["path"] = "gitlab"
    vault_data = hashi_vault_rundeck(**vdata)
    return vault_data["data"]["data"]["access_token"].get("sane_backups")


def getLBcredentials():
    """Get LB Credentials."""
    vdata["path"] = "loadbalancer_secrets"
    vault_data = hashi_vault_rundeck(**vdata)
    svcp = vault_data["data"]["data"]["svc_acc"].get("password")
    svcu = vault_data["data"]["data"]["svc_acc"].get("username")
    lowu = vault_data["data"]["data"]["f5_lower"].get("username")
    lowp = vault_data["data"]["data"]["f5_lower"].get("password")
    return svcp, svcu, lowu, lowp


def getNBtoken():
    """Get Nautobot token."""
    vdata["path"] = "nautobot"
    vault_data = hashi_vault_rundeck(**vdata)
    if "nautobot-cat.onefiserv.net" in nburl.lower():
        return vault_data["data"]["data"]["keys"].get("cat")
    elif "nautobot.onefiserv.net" in nburl.lower():
        return vault_data["data"]["data"]["keys"].get("prod")
