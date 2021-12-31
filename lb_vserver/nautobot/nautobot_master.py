from helper.script_conf import log
from nautobot.nautobot_fun import nautobot_fun


def nautobot_master(db, NB):
    """
    Create or Update all lb devices on nautobot
    1. Get or Create device (loadbalancer)
      1.1 Get or Create device-types
          1.1.1 Get - Manufacturer need to available
      1.2 Get or Create device_role
      1.3 Get or Create Site (Data dict need to be updated)
          1.3.1 Get or Create Region
    """
    doc_rec = "no_change"
    log.info(f"Updating device : {doc_rec}")
    devices = db.get_document("device", doc_rec)
    nbf = nautobot_fun(NB)
    for lb in devices:
        log.info(f"{lb.get('hostname')}")
        nbf.get_loadbalancer(lb)
    log.info("Updating device status to default..")
    db.update_host_status()

    """
    Create or Update all VIPs on nautobot
    """
    doc_rec = "delete"
    log.info(f"Updating VIP : {doc_rec}")
    vips = db.get_document("vip", doc_rec)
    for vip in vips:
        nbf.get_loadbalancer(vip.get("loadbalancer"))
        if hasattr(nbf, "lb_uuid"):
            log.info(f"LB Name: {vip.get('loadbalancer')}, VIP Name: {vip.get('name')}")
            nb_v = nautobot_fun(NB, nbf.lb_uuid)
            nb_v.write_data(vip)
            del nbf.get_loadbalancer.lb_uuid
        else:
            log.error(f"[{lb['hostname']}] not found on Nautobot")
    log.info("Updating VIP status to default..")
    db.update_vip_status()
    log.info("Update Complete")
