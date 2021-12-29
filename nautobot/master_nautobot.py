import os
from helper.script_conf import *
from nautobot_fun import nautobot_fun
from nautobot_client import NautobotClient
from helper.db_fun import MongoDB


log = LOG("master_nautobot")
npwd = os.environ.get("RD_OPTION_NAUTOBOT_KEY")
url = os.environ.get("RD_OPTION_NAUTOBOT_URL")
dbu = os.environ.get("RD_OPTION_DB_USER")
dbp = os.environ.get("RD_OPTION_DB_PWD")
dbh = os.environ.get("RD_OPTION_DB_HOST")
NB = NautobotClient(url, npwd)
db = MongoDB(dbu, dbp, dbh, log)

if __name__ == "__main__":
    """
    Create or Update all lb devices on nautobot
    1. Get or Create device (loadbalancer)
      1.1 Get or Create device-types
          1.1.1 Get - Manufacturer need to available
      1.2 Get or Create device_role
      1.3 Get or Create Site (Data dict need to be updated)
          1.3.1 Get or Create Region
    """
    devices = db.get_document("device", "no_change")
    nbf = nautobot_fun(NB, log)
    for lb in devices:
        # log.info(lb)
        nbf.get_loadbalancer(lb)
    db.update_host_status()

    """
    Create or Update all VIPs on nautobot
    """
    # del nbf.get_loadbalancer.lb_uuid
    vips = db.get_document("vip", "delete")
    for vip in vips:
        nbf.get_loadbalancer(vip.get("loadbalancer"))
        if hasattr(nbf, "lb_uuid"):
            log.info(f"LB Name: {vip.get('loadbalancer')}, VIP Name: {vip.get('name')}")
            nb_v = nautobot_fun(NB, log, nbf.lb_uuid)
            nb_v.write_data(vip)
            del nbf.get_loadbalancer.lb_uuid
        else:
            log.error(f"[{lb['hostname']}] not found on Nautobot")
    db.update_vip_status()
