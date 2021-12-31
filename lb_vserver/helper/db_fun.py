from pymongo import MongoClient
from deepdiff import DeepDiff as diff
from helper.script_conf import log


class MongoDB:
    def __init__(self, usr, pwd, host):
        self.log = log
        self.client = MongoClient(host=f"mongodb://{usr}:{pwd}@{host}/fdc_inventory?authSource=admin")
        self.log.debug("DB initiated")

    def vip_diff(self, lb_data):
        self.db = self.client.fdc_inventory.sane_devices
        query = {"hostname": lb_data.get("hostname"), "environment": lb_data.get("environment")}
        document = self.db.find_one(query)
        match = False
        if document:
            if not diff(document.get("vips"), lb_data.get("vips")):
                match = True
        return match

    def update_document(self, query, data):
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
        self.db = self.client.fdc_inventory.sane_devices
        query = {"address": lb_data.get("address"), "hostname": lb_data.get("hostname")}
        if "Netscaler" in lb_data.get("environment"):
            query = {"ns_ip_address": lb_data.get("ns_ip_address"), "hostname": lb_data.get("hostname")}
        self.update_document(query, lb_data)

    def vip_collection(self, vip_data):
        self.db = self.client.fdc_inventory.sane_lb_vip
        query = {
            "address": vip_data.get("address"),
            "port": vip_data.get("port"),
            "protocol": vip_data.get("protocol"),
            "environment": vip_data.get("environment"),
        }
        self.update_document(query, vip_data)

    def update_host_status(self):
        self.client.fdc_inventory.sane_devices.update_many(
            {}, {"$set": {"document_status": {"status": "delete", "rec": "no_change"}}}
        )

    def update_vip_status(self):
        self.client.fdc_inventory.sane_lb_vip.update_many(
            {}, {"$set": {"document_status": {"status": "delete", "rec": "no_change"}}}
        )

    def get_collection(self, col):
        if col == "device":
            self.db = self.client.fdc_inventory.sane_devices
        else:
            self.db = self.client.fdc_inventory.sane_lb_vip

    def get_document(self, col, query_state):
        self.get_collection(col)
        query = {"document_status.rec": query_state}
        return self.db.find(query)
