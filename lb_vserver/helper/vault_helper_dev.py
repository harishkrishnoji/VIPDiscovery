# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
from helper_fts.vault import hashi_vault


token = os.environ.get("HASHI_TOKEN")
nburl = os.environ.get("RD_OPTION_NAUTOBOT_URL")


def getGITtoken():
    """Get Git Token."""
    path = "gitlab"
    vault_data = hashi_vault(token=token, path=path)
    return vault_data["data"]["data"]["access_token"].get("sane_backups")


def getLBcredentials():
    """Get LB Credentials."""
    path = "loadbalancer_secrets"
    vault_data = hashi_vault(token=token, path=path)
    svcp = vault_data["data"]["data"]["svc_acc"].get("password")
    svcu = vault_data["data"]["data"]["svc_acc"].get("username")
    lowu = vault_data["data"]["data"]["f5_lower"].get("username")
    lowp = vault_data["data"]["data"]["f5_lower"].get("password")
    return svcp, svcu, lowu, lowp


def getNBtoken():
    """Get Nautobot Token."""
    path = "nautobot"
    vault_data = hashi_vault(token=token, path=path)
    if "nautobot-cat.onefiserv.net" in nburl.lower():
        return vault_data["data"]["data"]["keys"].get("cat")
    elif "nautobot.onefiserv.net" in nburl.lower():
        return vault_data["data"]["data"]["keys"].get("prod")
