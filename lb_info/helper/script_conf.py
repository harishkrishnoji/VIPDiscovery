import logging
import sys
import os


def LOG(name="OFD_NS_VIP"):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s | %(module)s | %(message)s", datefmt="%Y/%m/%d %H:%M:%S", stream=sys.stdout
    )
    log = logging.getLogger(name)
    log.setLevel(os.environ.get("RD_OPTION_LOG_LEVEL"))
    return log


VIP_FIELDS = list(["address", "port", "loadbalancer", "name", "pool"])

NS_DEVICE = list(
    [
        "ha_ip_address",
        "ha_master_state",
        "ipv4_address",
        "instance_state",
        "is_ha_configured",
        "mgmt_ip_address",
        "model_id",
        "hostname",
        "ns_ip_address",
        "serialnumber",
        "region",
        "system_hardwareversion",
        "type",
        "version",
    ]
)

F5_DEVICE = list(["uuid", "address", "product", "version", "hostname"])

F5_STANDALONE = list(["SLBAPP1", "OMA1GIOF5A"])

NS_API_DATA = dict([("proxy_key", "_MPS_API_PROXY_MANAGED_INSTANCE_IP")])

DISREGARD_VIP = list(["0.0.0.0", "1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5", ":0"])

DISREGARD_LB_F5 = list(
    [
        "VCD",
        "slbfde",
        "LAB",
        "OMA1GIOF5B-v1.giolab.local",
        "SLBSVC",
        "SLBAPP2",
        "SLBAPP3",
        "localhost",
        "INBOM1LTMSFM0",
        "SLBEDG01",
        "ecdbkel02-guest02", # ERROR DEVICES
        "ecdbkel01-guest02", # ERROR DEVICES
        "ecdbkel02-guest02.network.onefiserv.net", # ERROR DEVICES
        "ecddmzl02-guest02.network.onefiserv.net", # ERROR DEVICES
        "ecdbkel02.network.onefiserv.net", # ERROR DEVICES
        "ecdbkel01-guest02.network.onefiserv.net", # ERROR DEVICES
        "elidpxy03.onefiserv.net", # ERROR DEVICES
        "USIRT01SLBLWR01B.network.onefiserv.net", # ERROR DEVICES
        "ecddmzg02.fiserv.net", # ERROR DEVICES
        "ecddmz01-guest02.network.onefiserv.net", # ERROR DEVICES
        "elidpxy04.onefiserv.net", # ERROR DEVICES
        "jxpdapxy02.onefiserv.net", # ERROR DEVICES
    ]
)


DISREGARD_LB_CITRIX = list(
    [
        "AUSYD1SLBSFM01B-D2NR",
        "ARBNA2SLBSFM01B-D2NR",
        "USOMA1SLBINT03B",
        "INMUM1SLBSFM01A-C2",
        "USOMA1SLBSFA02A",
        "ARBNA2SLBSFM01B-TESTLEG",
        "AUSYD2SLBCOR01B-A2PL",
        "AUSYD2SLBSFM01B-A2R",
        "USCHD1SLBINT04B",
        "DEFRA2SLBCOR50a",
        "USCHD1SLBINT01B",
    ]
)

NAUTOBOT_DEVICE_ROLES = dict(
    [("LB", {"name": "load_balancer", "slug": "load-balancer", "description": "F5 and Citrix LB role"})]
)

NAUTOBOT_DEVICE_REGION = dict(
    [
        ("INMUM1", {"region": "India", "site": "bom01"}),
        ("INBOM1", {"region": "India", "site": "bom01"}),
        ("DEFRA2", {"region": "Germany", "site": "fra02"}),
        ("DERFA2", {"region": "Germany", "site": "fra02"}),
        ("DEFRA1", {"region": "Germany", "site": "fra01"}),
        ("BRHTL1", {"region": "Brazil", "site": "htl01"}),
        ("USCHD1", {"region": "United States", "site": "chd01"}),
        ("ARBNA1", {"region": "Argentina", "site": "fra02"}),
        ("LAB1AK", {"region": "United States", "site": "oma01"}),
        ("BRSPA2", {"region": "Brazil", "site": "spa02"}),
        ("USOMA1", {"region": "United States", "site": "oma01"}),
        ("AUSYD2", {"region": "Australia", "site": "syd02"}),
        ("ARBNA2", {"region": "Argentina", "site": "bna02"}),
        ("AUSYD1", {"region": "Australia", "site": "syd01"}),
        ("SANE_UNK", {"region": "United States", "site": "SANE_UNK", "description": "SANE - UNKNOWN SITE"}),
    ]
)

NAUTOBOT_DEVICE_REGION_OFS = dict(
    [
        ("10.14", {"region": "United States", "site": "phx01", "description": "Phoenix"}),
        ("10.144", {"region": "United States", "site": "slc01", "description": "Salt Lake City"}),
        ("10.26", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.48", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.165", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.172", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.175", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.203", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.206", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("10.103", {"region": "United States", "site": "lwv01", "description": "Lewisville CORP"}),
        ("10.173", {"region": "United States", "site": "cal01", "description": "Calgary, Canada"}),
        ("10.174", {"region": "United States", "site": "mis01", "description": "Mississauga, Canada"}),
        ("10.2", {"region": "United States", "site": "irv01", "description": "Irving CORP Dev/QA"}),
        ("10.105", {"region": "United States", "site": "irv01", "description": "Irving Card service"}),
        ("10.215", {"region": "United States", "site": "tgx01", "description": "Troy Galaxy"}),
        ("10.224", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("10.227", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("10.154", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("10.36", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("10.93", {"region": "United States", "site": "jhc01", "description": "Johns Creek Midori"}),
        ("10.92", {"region": "United States", "site": "jhc01", "description": "Johns Creek Midori"}),
        ("10.134", {"region": "United States", "site": "jhc01", "description": "Johns Creek CORP"}),
        ("10.226", {"region": "United States", "site": "crh01", "description": "Cherry Hill"}),
        ("10.23", {"region": "United States", "site": "dub01", "description": "Dublin"}),
        ("10.236", {"region": "United States", "site": "crh_lwr01", "description": "Cherry Hill Lower"}),
        ("10.31", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("10.35", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("172.25", {"region": "United States", "site": "haw01", "description": "Hawaii"}),
        ("10.182", {"region": "United States", "site": "cor01", "description": "Corporate"}),
        ("10.46", {"region": "United States", "site": "brk01", "description": "Brookfield"}),
        ("10.109", {"region": "United States", "site": "mad01", "description": "Madison"}),
        ("11.14", {"region": "United States", "site": "phx01", "description": "Phoenix"}),
        ("11.144", {"region": "United States", "site": "slc01", "description": "Salt Lake City"}),
        ("11.26", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.48", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.165", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.172", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.175", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.203", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.206", {"region": "United States", "site": "lwv01", "description": "Lewisville"}),
        ("11.103", {"region": "United States", "site": "lwv01", "description": "Lewisville CORP"}),
        ("11.173", {"region": "United States", "site": "cal01", "description": "Calgary, Canada"}),
        ("11.174", {"region": "United States", "site": "mis01", "description": "Mississauga, Canada"}),
        ("11.2", {"region": "United States", "site": "irv01", "description": "Irving CORP Dev/QA"}),
        ("11.105", {"region": "United States", "site": "irv01", "description": "Irving Card service"}),
        ("11.215", {"region": "United States", "site": "tgx01", "description": "Troy Galaxy"}),
        ("11.224", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("11.227", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("11.154", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("11.36", {"region": "United States", "site": "jhc01", "description": "Johns Creek"}),
        ("11.93", {"region": "United States", "site": "jhc01", "description": "Johns Creek Midori"}),
        ("11.92", {"region": "United States", "site": "jhc01", "description": "Johns Creek Midori"}),
        ("11.134", {"region": "United States", "site": "jhc01", "description": "Johns Creek CORP"}),
        ("11.226", {"region": "United States", "site": "crh01", "description": "Cherry Hill"}),
        ("11.23", {"region": "United States", "site": "dub01", "description": "Dublin"}),
        ("11.236", {"region": "United States", "site": "crh_lwr01", "description": "Cherry Hill Lower"}),
        ("11.31", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("11.35", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("172.25", {"region": "United States", "site": "haw01", "description": "Hawaii"}),
        ("11.182", {"region": "United States", "site": "cor01", "description": "Corporate"}),
        ("11.46", {"region": "United States", "site": "brk01", "description": "Brookfield"}),
        ("11.109", {"region": "United States", "site": "mad01", "description": "Madison"}),
    ]
)
