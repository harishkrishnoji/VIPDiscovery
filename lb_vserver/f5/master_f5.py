import os
import json
from f5_bigiq.client import BigIQClient
from helper.script_conf import *
from f5_fun import F5HelperFun
from helper.db_fun import MongoDB

log = LOG("f5_master")

ENV = os.environ.get("RD_OPTION_ENV")
svcp = os.environ.get("RD_OPTION_SVC_PWD")
svcu = os.environ.get("RD_OPTION_SVC_USER")
lowu = os.environ.get("RD_OPTION_LOWER_USER")
lowp = os.environ.get("RD_OPTION_LOWER_PWD")
dbp = os.environ.get("RD_OPTION_DB_PWD")
dbu = os.environ.get("RD_OPTION_DB_USER")
dbh = os.environ.get("RD_OPTION_DB_HOST")


def f5_master(f5, tags, ENV, db):
    """
    Get list of all devices from BIG-IQ, which are reachable from BIG-IQ.
    Check if it is not in DISREGAR_LB_F5 list and HA state to be standby.
    Pass the list to "F5HelperFun" Class to gather all VIP related details.
    """

    for item in device_list(f5):
        log.info(f"{item['hostname']}")
        discard = False
        item["tags"] = tags
        item["type"] = "ltm"
        item["environment"] = ENV
        for (i, ig) in enumerate(DISREGARD_LB_F5):
            if DISREGARD_LB_F5[i] in item["hostname"]:
                discard = True
        if not discard and item.get("status") == "Active":
            ha_state = device_ha_state(f5, item, "standby")
            if ha_state == "active":
                item["ha_state"] = ha_state
            elif ha_state == "standby":
                item["ha_state"] = ha_state
                f5f = F5HelperFun(f5, item)
                if f5f.apidata:
                    item["vips"] = f5f.gather_vip_info()
                else:
                    log.error(f"{item['hostname']}: Gathering Pool and Cert info")
        db.host_collection(item)
        for vip in item.get("vips", []):
            db.vip_collection(vip)


def device_list(f5):
    """function to pull devices which are reachable from BIG-IQ.
    """
    resp = f5.bigiq_api_call()
    log.debug(f"F5 Device list Status code : {resp.status_code}")
    if resp.status_code == 200:
        jresp = json.loads(resp.text)
        return device_stats(f5, list(dict((i, j[i]) for i in F5_DEVICE) for j in jresp["items"]))


def device_ha_state(f5, item, state):
    """function to get the HA state for given device.
    """
    discard = False
    for (i, ig) in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i] in item["hostname"]:
            discard = True
    if not discard:
        try:
            resp = f5.bigiq_api_call("GET", uuid=item["uuid"], path="/rest-proxy/mgmt/tm/sys/failover")
            if resp.status_code == 200:
                return json.loads(resp.text)["apiRawValues"]["apiAnonymous"].split()[1]
            else:
                log.error(f"{item['hostname']} : {path} : {resp.status_code}")
        except:
            log.error(f"{item['hostname']}")
    else:
        return discard


def device_stats(f5, f5_info):
    """function to pull devices which are reachable from BIG-IQ.
    """
    resp = f5.bigiq_api_call("GET", uuid="stats")
    if resp.status_code == 200:
        jresp = json.loads(resp.text)
        for item in f5_info:
            svalue = f"https://localhost/mgmt/shared/resolver/device-groups/cm-bigip-allBigIpDevices/devices/{item['uuid']}/stats"
            if "unavailable" in str(jresp["entries"][svalue]["nestedStats"]["entries"]["health.summary"]):
                item["status"] = "Unreachable"
                log.error(f"Unreachable Device : {item['hostname']}")
            else:
                item["status"] = "Active"
        return f5_info
    else:
        log.error(f"{uuid} : {resp.status_code}")


if __name__ == "__main__":
    if ENV == "OFD_F5":
        f5 = BigIQClient("https://10.165.232.72/mgmt/", svcu, svcp, "ACS-RADIUS")
        tags = ["ofd", "f5"]
    elif ENV == "OFS_F5":
        f5 = BigIQClient("https://11.224.134.85/mgmt/", svcu, svcp, "ClearPass")
        tags = ["ofs", "f5"]
    elif ENV == "OFS_F5_Lower":
        f5 = BigIQClient("https://11.35.169.85/mgmt/", lowu, lowp, "TACACS+")
        tags = ["ofs", "f5", "lowers"]
    db = MongoDB(dbu, dbp, dbh, log)
    f5_master(f5, tags, ENV, db)
