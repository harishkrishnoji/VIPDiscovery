import logging

# import sys
import os


# logging.basicConfig(
#    format="%(asctime)s %(levelname)s | %(module)s | %(message)s", datefmt="%Y/%m/%d %H:%M:%S", stream=sys.stdout
# )


def LOG(name="VIP", file="data/vip.log"):
    log = logging.getLogger(name)
    if os.environ.get("RD_OPTION_LOG_LEVEL") == "DEBUG":
        log.setLevel(logging.DEBUG)
    elif os.environ.get("RD_OPTION_LOG_LEVEL") == "ERROR":
        log.setLevel(logging.ERROR)
    else:
        log.setLevel(logging.INFO)

    format = "%(asctime)s %(levelname)s | %(module)s | %(message)s"
    formatter = logging.Formatter(format)
    file_handler = logging.FileHandler(file)
    # stream_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    # file_handler.setStream(stream_handler)
    log.addHandler(file_handler)
    return log


#########################################################################
#   Mandatory keys/value required to create VIP in Nautobot
#########################################################################

VIP_FIELDS = list(["address", "port", "loadbalancer", "name", "pool"])


#########################################################################
#   List of Keys/values which need to be collected from ADM
#########################################################################

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
        "system_hardwareversion",
        "type",
        "version",
    ]
)

#########################################################################
#   List of Keys/values which need to be collected from BIG-IQ
#########################################################################

F5_DEVICE = list(["uuid", "address", "product", "version", "hostname"])

#########################################################################
#   F5 Standalone devices
#########################################################################

F5_STANDALONE = list(["SLBAPP1", "OMA1GIOF5A"])

#########################################################################
#   Netscaler API Proxy Variable
#########################################################################

NS_API_DATA = dict([("proxy_key", "_MPS_API_PROXY_MANAGED_INSTANCE_IP")])

#########################################################################
#   List of VIPs which need to be disregarded from F5 devices
#########################################################################

DISREGARD_VIP = list(["0.0.0.0", "1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5", ":0"])

#########################################################################
#   List of LB instances to disregard
#########################################################################

DISREGARD_LB_F5 = list(
    [
        # "VCD",      # VPN and VDI Instances
        "slbfde",  # FDE Instances
        # "LAB",      # LAB Instances
        "OMA1GIOF5B-v1.giolab.local",
        # "SLBSVC",
        "SLBAPP2",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "SLBAPP3",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "localhost",
        # "SLBEDG01",
        # OFS Devices
        "ecdbkel02-guest02",  # ERROR DEVICES
        "ecdbkel01-guest02",  # ERROR DEVICES
        "ecdbkel02-guest02.network.onefiserv.net",  # ERROR DEVICES
        "ecddmzl02-guest02.network.onefiserv.net",  # ERROR DEVICES
        "ecdbkel02.network.onefiserv.net",  # ERROR DEVICES
        "ecdbkel01-guest02.network.onefiserv.net",  # ERROR DEVICES
        "elidpxy03.onefiserv.net",  # ERROR DEVICES
        "USIRT01SLBLWR01B.network.onefiserv.net",  # ERROR DEVICES
        "ecddmzg02.fiserv.net",  # ERROR DEVICES
        "ecddmz01-guest02.network.onefiserv.net",  # ERROR DEVICES
        "elidpxy04.onefiserv.net",  # ERROR DEVICES
        "jxpdapxy02.onefiserv.net",  # ERROR DEVICES
    ]
)

DISREGARD_LB_CITRIX = []

#########################################################################
#   Nautobot Variabes
#########################################################################

NAUTOBOT_DEVICE_ROLES = dict(
    [("LB", {"name": "load_balancer", "slug": "load-balancer", "description": "F5 and Citrix LB role"})]
)

NAUTOBOT_DEVICE_REGION = dict(
    [
        ("INMUM1", {"region": "India", "site": "INBOM01"}),
        ("INBOM1", {"region": "India", "site": "INBOM01"}),
        ("DEFRA2", {"region": "Germany", "site": "DEFRA02"}),
        ("DERFA2", {"region": "Germany", "site": "DEFRA02"}),
        ("DEFRA1", {"region": "Germany", "site": "DEFRA01"}),
        ("BRHTL1", {"region": "Brazil", "site": "BRHTL01"}),
        ("USCHD1", {"region": "United States", "site": "USCHD01"}),
        ("ARBNA1", {"region": "Argentina", "site": "ARBNA01"}),
        ("LAB1AK", {"region": "United States", "site": "USOMA01"}),
        ("BRSPA2", {"region": "Brazil", "site": "BRSPA01"}),
        ("USOMA1", {"region": "United States", "site": "USOMA01"}),
        ("USCHI2", {"region": "United States", "site": "USCHI02"}),
        ("USCHI0", {"region": "United States", "site": "USCHI02"}),
        ("USDAL3", {"region": "United States", "site": "USDAL03"}),
        ("AUSYD2", {"region": "Australia", "site": "AUSYD02"}),
        ("ARBNA2", {"region": "Argentina", "site": "ARBNA02"}),
        ("AUSYD1", {"region": "Australia", "site": "AUSYD01"}),
        ("SANE_UNK", {"region": "United States", "site": "USOMA01"}),
    ]
)

NAUTOBOT_DEVICE_REGION_OFS = dict(
    [
        ("10.14", {"region": "United States", "site": "USCHD02"}),
        ("10.144", {"region": "United States", "site": "slc01", "description": "Salt Lake City"}),
        ("10.26", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.48", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.165", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.172", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.175", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.203", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.206", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("10.103", {"region": "United States", "site": "USLJV04", "description": "Lewisville CORP"}),
        ("10.173", {"region": "United States", "site": "cal01", "description": "Calgary, Canada"}),
        ("10.174", {"region": "United States", "site": "CAMIS01", "description": "Mississauga, Canada"}),
        ("10.2", {"region": "United States", "site": "USIRT02", "description": "Irving CORP Dev/QA"}),
        ("10.105", {"region": "United States", "site": "USIRT02", "description": "Irving Card service"}),
        ("10.215", {"region": "United States", "site": "USTYM01", "description": "Troy Galaxy"}),
        ("10.224", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("10.227", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("10.154", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("10.36", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("10.93", {"region": "United States", "site": "USJC201", "description": "Johns Creek Midori"}),
        ("10.92", {"region": "United States", "site": "USJC201", "description": "Johns Creek Midori"}),
        ("10.134", {"region": "United States", "site": "USJC201", "description": "Johns Creek CORP"}),
        ("10.226", {"region": "United States", "site": "USCHX01", "description": "Cherry Hill"}),
        ("10.23", {"region": "United States", "site": "IEDUB1", "description": "Dublin"}),
        ("10.236", {"region": "United States", "site": "USCHX01", "description": "Cherry Hill Lower"}),
        ("10.31", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("10.35", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("172.25", {"region": "United States", "site": "haw01", "description": "Hawaii"}),
        ("10.182", {"region": "United States", "site": "cor01", "description": "Corporate"}),
        ("10.46", {"region": "United States", "site": "brk01", "description": "Brookfield"}),
        ("10.109", {"region": "United States", "site": "mad01", "description": "Madison"}),
        ("11.14", {"region": "United States", "site": "phx01", "description": "Phoenix"}),
        ("11.144", {"region": "United States", "site": "slc01", "description": "Salt Lake City"}),
        ("11.26", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.48", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.165", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.172", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.175", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.203", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.206", {"region": "United States", "site": "USLJV04", "description": "Lewisville"}),
        ("11.103", {"region": "United States", "site": "USLJV04", "description": "Lewisville CORP"}),
        ("11.173", {"region": "United States", "site": "cal01", "description": "Calgary, Canada"}),
        ("11.174", {"region": "United States", "site": "CAMIS01", "description": "Mississauga, Canada"}),
        ("11.2", {"region": "United States", "site": "USIRT02", "description": "Irving CORP Dev/QA"}),
        ("11.105", {"region": "United States", "site": "USIRT02", "description": "Irving Card service"}),
        ("11.215", {"region": "United States", "site": "USTYM01", "description": "Troy Galaxy"}),
        ("11.224", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("11.227", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("11.154", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("11.36", {"region": "United States", "site": "USJC201", "description": "Johns Creek"}),
        ("11.93", {"region": "United States", "site": "USJC201", "description": "Johns Creek Midori"}),
        ("11.92", {"region": "United States", "site": "USJC201", "description": "Johns Creek Midori"}),
        ("11.134", {"region": "United States", "site": "USJC201", "description": "Johns Creek CORP"}),
        ("11.226", {"region": "United States", "site": "USCHX01", "description": "Cherry Hill"}),
        ("11.23", {"region": "United States", "site": "IEDUB1", "description": "Dublin"}),
        ("11.236", {"region": "United States", "site": "USCHX01", "description": "Cherry Hill Lower"}),
        ("11.31", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("11.35", {"region": "United States", "site": "lwr01", "description": "Lowers"}),
        ("172.25", {"region": "United States", "site": "haw01", "description": "Hawaii"}),
        ("11.182", {"region": "United States", "site": "cor01", "description": "Corporate"}),
        ("11.46", {"region": "United States", "site": "brk01", "description": "Brookfield"}),
        ("11.109", {"region": "United States", "site": "mad01", "description": "Madison"}),
    ]
)
