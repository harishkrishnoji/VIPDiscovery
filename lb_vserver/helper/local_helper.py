# pylint: disable=W1203, C0103, W0631
"""Script local config."""

import os
import requests
from helper_fts.logger import get_logger
from pymongo import MongoClient

log = get_logger()


def uploadfile(fname):
    """Upload file to remote server.

    Args:
        fname (str): Filename which need to be uploaded
    """
    url = "https://sas-automation.1dc.com/cgi-bin/uploadfile.py"
    files = [("filename", (os.path.basename(fname), open(fname, "rb")))]
    response = requests.request("POST", url, files=files, verify=False)
    return response.text


class MongoDB:
    """Create a MongoDB API client."""

    def __init__(self, usr, pwd, host):
        """Initialize MongoDB API Client.

        Args:
            usr (str): Username to authenticate to MongoDB API.
            pwd (str): Password to authenticate to MongoDB API.
            host (str): MongoDB host.
        """
        self.log = log
        self.client = MongoClient(host=f"mongodb://{usr}:{pwd}@{host}/fdc_inventory?authSource=admin")
        self.log.debug("DB initiated")
        self.db = ""

    def update_document(self, query, data):
        """Update document on MongoDB if diff condition pass.

        Args:
            query (str): DB query string.
            data (dict): data to run diff function.
        """
        document = self.db.find_one(query)
        if document:
            document.pop("_id", None)
            self.db.replace_one(query, data)
        else:
            self.db.insert_one(data)

    def host_collection(self, lb_data):
        """Get Device collection from MongoDB.

        Args:
            lb_data (dict): LB Device related info.
        """
        self.db = self.client.fdc_inventory.sane_devices
        query = {"mgmt_address": lb_data.get("mgmt_address"), "hostname": lb_data.get("hostname")}
        self.update_document(query, lb_data)

    def vip_collection(self, vips):
        """Get VIP collection from MongoDB.

        Args:
            vips (dict): VIP related info.
        """
        self.db = self.client.fdc_inventory.sane_lb_vip
        for vip_data in vips:
            query = {
                "address": vip_data.get("address"),
                "port": vip_data.get("port"),
                "protocol": vip_data.get("protocol"),
                "environment": vip_data.get("environment"),
            }
            self.update_document(query, vip_data)
