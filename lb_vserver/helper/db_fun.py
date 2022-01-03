# pylint: disable=W1203, C0103, W0631
"""MongoDB Function."""

from deepdiff import DeepDiff as diff
from pymongo import MongoClient
from helper.script_conf import log


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

    def vip_diff(self, lb_data):
        """Find if VIP info is same as DB VIP info.

        Args:
            lb_data (dic): LB info including VIPs.

        Returns:
            bool: State of match. True or False.
        """
        self.db = self.client.fdc_inventory.sane_devices
        query = {"hostname": lb_data.get("hostname"), "environment": lb_data.get("environment")}
        document = self.db.find_one(query)
        match = False
        if document:
            if not diff(document.get("vips"), lb_data.get("vips")):
                match = True
        return match

    def update_document(self, query, data):
        """Update document on MongoDB if diff condition pass.

        Args:
            query (str): DB query string.
            data (dict): data to run diff function.
        """
        document = self.db.find_one(query)
        if document:
            document.pop("_id", None)
            if diff(document, data, exclude_paths=["root['document_status']"]):
                data["document_status"] = {"rec": "update", "status": "active"}
                self.db.replace_one(query, data)
            else:
                self.db.update_one(query, {"$set": {"document_status.status": "active"}})
        else:
            data["document_status"] = {"rec": "update", "status": "active"}
            self.db.insert_one(data)

    def host_collection(self, lb_data):
        """Get Device collection from MongoDB.

        Args:
            lb_data (dict): LB Device related info.
        """
        self.db = self.client.fdc_inventory.sane_devices
        query = {"address": lb_data.get("address"), "hostname": lb_data.get("hostname")}
        if "Netscaler" in lb_data.get("environment"):
            query = {"ns_ip_address": lb_data.get("ns_ip_address"), "hostname": lb_data.get("hostname")}
        self.update_document(query, lb_data)

    def vip_collection(self, vip_data):
        """Get VIP collection from MongoDB.

        Args:
            vip_data (dict): VIP related info
        """
        self.db = self.client.fdc_inventory.sane_lb_vip
        query = {
            "address": vip_data.get("address"),
            "port": vip_data.get("port"),
            "protocol": vip_data.get("protocol"),
            "environment": vip_data.get("environment"),
        }
        self.update_document(query, vip_data)

    def update_host_status(self):
        """Update host document_state after pulling diff info into nautobot."""
        self.client.fdc_inventory.sane_devices.update_many(
            {}, {"$set": {"document_status": {"status": "delete", "rec": "no_change"}}}
        )

    def update_vip_status(self):
        """Update VIP document_state after pulling diff info into nautobot."""
        self.client.fdc_inventory.sane_lb_vip.update_many(
            {}, {"$set": {"document_status": {"status": "delete", "rec": "no_change"}}}
        )

    def get_collection(self, col):
        """Get DB collection.

        Args:
            col (str): Collection name.
        """
        if col == "device":
            self.db = self.client.fdc_inventory.sane_devices
        else:
            self.db = self.client.fdc_inventory.sane_lb_vip

    def get_document(self, col, query_state):
        """Get document from specific collection.

        Args:
            col (str): Collection name.
            query_state (str): document_status req query string.

        Returns:
            dict: document which match the query.
        """
        self.get_collection(col)
        query = {"document_status.rec": query_state}
        return self.db.find(query)
