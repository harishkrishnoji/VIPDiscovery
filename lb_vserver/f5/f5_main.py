# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710
"""F5 Master."""

import sys
import json
import requests
from helper.local_helper import log, uploadfile, getfile
from f5.f5_filters import filter_device, filter_device1, filter_standalone
from helper.variables_lb import F5_DEVICE_FIELDS
from nautobot.nautobot_main import NautobotClient
from f5.f5_fun import F5HelperFun


class F5_MAIN:
    """Gather all F5 device list from BigIQ, run through filter."""

    def __init__(self, f5, tags, env) -> None:
        """Initialize."""
        self.f5 = f5
        self.tags = tags
        self.env = env
        self.sas_vip_info = []
        self.f5f = ""
        self.f5_main()

    def f5_main(self):
        """Gather all F5 device list from BigIQ, run through filter."""
        for item in self.device_list():
            item["mgmt_address"] = item.pop("address")
            item["tags"] = self.tags
            item["type"] = "ltm"
            item["environment"] = self.env
            if not filter_device1(item) and item.get("status") == "Active":
                ha_state = self.device_ha_state(item)
                if ha_state:
                    self.f5f = F5HelperFun(self.f5, item)
                if ha_state == "active":
                    item["ha_master_state"] = ha_state
                elif ha_state == "standby" or ha_state == "Standalone":
                    item["ha_master_state"] = ha_state
                    self.f5f.item = item
                    item["vips"] = self.f5f.gather_vip_info()
                    if item["vips"]:
                        log.info(f"{item.get('hostname')}: [VIPs] {len(item['vips'])}")
                        self.sas_vip_info.extend(item["vips"])
                        NautobotClient(item)
        self.update_records()
        log.info("Job done")

    def update_records(self):
        """Update VIP data on to remote server and Nautobot."""
        filename = f"{self.env}.json"
        with open(filename, "w+") as json_file:
            json.dump(self.sas_vip_info, json_file, indent=4, separators=(",", ": "), sort_keys=True)
        oldfile = getfile(filename)
        if oldfile:
            with open(f"{filename}-old", "w+") as json_file:
                json.dump(oldfile, json_file, indent=4, separators=(",", ": "), sort_keys=True)
        resp = uploadfile(filename)
        log.info(resp.strip())

    def device_list(self):
        """Get list of all devices from BIG-IQ."""
        try:
            jresp = json.loads(self.f5.bigiq_api_call().text)
            log.info(f"F5 Device count : {len(jresp.get('items'))}")
            device_info = []
            for device in jresp["items"]:
                if filter_device(device):
                    device_info.append(dict((i, device.get(i)) for i in F5_DEVICE_FIELDS))
            return self.device_stats(device_info)
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {err}")

    def device_ha_state(self, item):
        """Get the HA state for given device."""
        if not filter_standalone(item):
            try:
                resp = self.f5.bigiq_api_call("GET", uuid=item["uuid"], path="/rest-proxy/mgmt/tm/sys/failover")
                return json.loads(resp.text)["apiRawValues"]["apiAnonymous"].split()[1]
            except requests.exceptions.HTTPError:
                log.error(f"{sys._getframe().f_code.co_name}: Service Unavailable : {item['hostname']}")
            except Exception as err:
                log.error(f"{sys._getframe().f_code.co_name}: {item['hostname']}: {err}")
        else:
            return "Standalone"

    def device_stats(self, f5_info):
        """Check if list of all devices from BIG-IQ are reachable from BIG-IQ."""
        try:
            resp = self.f5.bigiq_api_call("GET", uuid="stats")
            jresp = json.loads(resp.text)
            for item in f5_info:
                svalue = f"https://localhost/mgmt/shared/resolver/device-groups/cm-bigip-allBigIpDevices/devices/{item['uuid']}/stats"
                if "unavailable" in str(jresp["entries"][svalue]["nestedStats"]["entries"].get("health.summary")):
                    item["status"] = "Unreachable"
                    item["ha_master_state"] = "Unreachable"
                    log.error(f"Unreachable Device : {item.get('hostname')}")
                else:
                    item["status"] = "Active"
            return f5_info
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {item['hostname']}: {err}")
