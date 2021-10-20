import json
from helper.script_conf import *
from helper.f5_fun import F5HelperFun

log = LOG("master_f5")


def f5_master(f5, NB, ENV):
    # Get F5 VIP details
    for item in device_list(f5):
        discard = False
        for (i, ig) in enumerate(DISREGARD_LB_F5):
            if DISREGARD_LB_F5[i] in item["hostname"]:
                discard = True
        if discard is False and item["state"] == "Active":
            if device_ha_state(f5, item, "standby") == "standby":
                log.info(f"Gathering VIPs from {item['hostname']}")
                f5f = F5HelperFun(f5, item, ENV)
                f5f.gather_vip_info(NB)


def device_list(f5):
    resp = f5.bigiq_api_call()
    log.debug(f"F5 Device list Status code : {resp.status_code}")
    if resp.status_code == 200:
        jresp = json.loads(resp.text)
        return device_stats(f5, list(dict((i, j[i]) for i in F5_DEVICE) for j in jresp["items"]))


def device_ha_state(f5, item, state):
    discard = False
    for (i, ig) in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i] in item["hostname"]:
            discard = True
    if discard is False:
        resp = f5.bigiq_api_call("GET", uuid=item["uuid"], path="/rest-proxy/mgmt/tm/sys/failover")
        if resp.status_code == 200:
            return json.loads(resp.text)["apiRawValues"]["apiAnonymous"].split()[1]
        else:
            log.error(f"{item['hostname']} : {path} : {resp.status_code}")
    else:
        return state


def device_stats(f5, f5_info):
    resp = f5.bigiq_api_call("GET", uuid="stats")
    if resp.status_code == 200:
        jresp = json.loads(resp.text)
        for item in f5_info:
            svalue = f"https://localhost/mgmt/shared/resolver/device-groups/cm-bigip-allBigIpDevices/devices/{item['uuid']}/stats"
            if "unavailable" in str(jresp["entries"][svalue]["nestedStats"]["entries"]["health.summary"]):
                item["state"] = "Unreachable"
                log.error(f"Unreachable Device : {item['hostname']}")
            else:
                item["state"] = "Active"
        return f5_info
    else:
        log.error(f"{uuid} : {resp.status_code}")
