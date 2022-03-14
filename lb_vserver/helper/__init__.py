"""Initilizer."""

import os
import json
from helper.gitlab_helper import GitLab_Client
from helper_fts.logger import get_logger
from helper.vault_helper import getGITtoken, getNBtoken, getLBcredentials

# from helper.vault_helper_dev import getGITtoken, getNBtoken, getLBcredentials

lfile = f"{os.getcwd()}/lfile.log"
log = get_logger("lfile")
edata = []
nburl = os.environ.get("RD_OPTION_NAUTOBOT_URL")
env = os.environ.get("RD_OPTION_ENV")
deviceToQuery = os.environ.get("RD_OPTION_DEVICES", "All")
glab = GitLab_Client(token=getGITtoken(), filepath=f"lb-vip/{env}.json")
gitFile = json.loads(glab.get_file().decode()) if glab.get_file() else ""
