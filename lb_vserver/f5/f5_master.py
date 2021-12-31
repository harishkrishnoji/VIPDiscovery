import json
from helper.script_conf import *
from f5.f5_fun import F5HelperFun


def f5_master(f5, tags, ENV, db):
    """
    Get list of all devices from BIG-IQ, which are reachable from BIG-IQ.
    Check if it is not in DISREGAR_LB_F5 list and HA state to be standby.
    Pass the list to "F5HelperFun" Class to gather all VIP related details.
    """
    log.debug("Master F5 Initiated.. ")
    log.debug(f"Gather Device list for {ENV}..")
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
            ha_state = device_ha_state(f5, item)
            if ha_state == "active":
                item["ha_state"] = ha_state
            elif ha_state == "standby":
                item["ha_state"] = ha_state
                f5f = F5HelperFun(f5, item)
                if f5f.apidata:
                    item["vips"] = f5f.gather_vip_info()
                else:
                    log.error(f"{item['hostname']}: Gathering Pool and Cert info")
        match = db.vip_diff(item)
        log.debug(f"{item.get('hostname')}: Device info DB Update...")
        db.host_collection(item)
        if not match:
            log.debug(f"{item.get('hostname')}: VIP info DB Update...")
            for vip in item.get("vips", []):
                db.vip_collection(vip)
        else:
            log.debug(f"{item.get('hostname')}: NO change in VIP info")


def device_list(f5):
    """function to pull devices which are reachable from BIG-IQ.
    """
    try:
        resp = f5.bigiq_api_call()
        jresp = json.loads(resp.text)
        log.debug(f"F5 Device count : {len(jresp.get('items'))}")
        return device_stats(f5, list(dict((i, j[i]) for i in F5_DEVICE) for j in jresp["items"]))
    except Exception as err:
        log.error(f"{err}")


def device_ha_state(f5, item):
    """function to get the HA state for given device.
    """
    discard = False
    for (i, ig) in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i] in item["hostname"]:
            discard = True
    if not discard:
        try:
            resp = f5.bigiq_api_call("GET", uuid=item["uuid"], path="/rest-proxy/mgmt/tm/sys/failover")
            return json.loads(resp.text)["apiRawValues"]["apiAnonymous"].split()[1]
        except Exception as err:
            log.error(f"{item['hostname']}: {err}")
    else:
        return discard


def device_stats(f5, f5_info):
    """function to pull devices which are reachable from BIG-IQ.
    """
    try:
        resp = f5.bigiq_api_call("GET", uuid="stats")
        jresp = json.loads(resp.text)
        for item in f5_info:
            svalue = f"https://localhost/mgmt/shared/resolver/device-groups/cm-bigip-allBigIpDevices/devices/{item['uuid']}/stats"
            if "unavailable" in str(jresp["entries"][svalue]["nestedStats"]["entries"]["health.summary"]):
                item["status"] = "Unreachable"
                log.error(f"Unreachable Device : {item['hostname']}")
            else:
                item["status"] = "Active"
        return f5_info
    except Exception as err:
        log.error(f"{item['hostname']}: {err}")
