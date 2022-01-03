# pylint: disable=W1203, C0103, W0631
"""Nautobot Master."""

from helper.script_conf import log
from nautobot.nautobot_fun import nautobot_fun

# document_state:
#     rec: Status of document/record has been updated or not.
#     status: Status of document/record if it active or need to be deleted.

DOC_REC_DEVICE = "no_change"
DOC_REC_VIP = "delete"


def nautobot_master(db, NB):
    """Create or Update all lb devices on nautobot. Create or Update all VIPs on nautobot."""
    log.info(f"Updating device : {DOC_REC_DEVICE}")
    devices = db.get_document("device", DOC_REC_DEVICE)
    nbf = nautobot_fun(NB)
    for lb in devices:
        log.info(f"{lb.get('hostname')}")
        nbf.get_loadbalancer(lb)
    log.info("Updating device status to default..")
    db.update_host_status()
    log.info(f"Updating VIP : {DOC_REC_VIP}")
    vips = db.get_document("vip", DOC_REC_VIP)
    for vip in vips:
        nbf.get_loadbalancer(vip.get("loadbalancer"))
        if hasattr(nbf, "lb_uuid"):
            log.info(f"LB Name: {vip.get('loadbalancer')}, VIP Name: {vip.get('name')}")
            nb_v = nautobot_fun(NB, nbf.lb_uuid)
            nb_v.main_fun(vip)
            del nbf.lb_uuid
        else:
            log.error(f"[{lb['hostname']}] not found on Nautobot")
    log.info("Updating VIP status to default..")
    db.update_vip_status()
    log.info("Update Complete")
