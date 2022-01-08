# pylint: disable=W1203, C0103, W0631
"""Script local config."""

#########################################################################
#   Mandatory keys/value required to create VIP in Nautobot
#########################################################################

VIP_FIELDS = list(["address", "port", "loadbalancer", "name", "pool", "pool_mem"])

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
#   List of Devices to pull data from BIG-IQ
#########################################################################

F5_DEVICE_TO_QUERY = list(["USOMA1ASMINT02A.1dc.com"])

#########################################################################
#   List of Keys/values which need to be collected from BIG-IQ
#########################################################################

F5_DEVICE_FIELDS = list(["uuid", "address", "product", "version", "hostname"])

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
        "slbfde",  # FDE Instances
        "OMA1GIOF5B-v1.giolab.local",
        "SLBAPP2",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "SLBAPP3",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "localhost",
        # "USCHI2SLBEDG01B.1dc.com",
        # "USDAL3SLBSVC1A.1dc.com",
        # "ARBNA1ASMINT01A.1dc.com",
        # "AUSYD1ASMINT01A.1dc.com",
        # "ARBNA1ASMINT02B.1dc.com",
        # "DEFRA2ASMINT01A.1dc.com",
        # "DEFRA1ASMINT01B.1dc.com",
        # "jcpmidlb01a.onefiserv.net",
        # "PLPIA1ASMINT01B.1dc.com",
        # "BRSPA2SLBSFM51B.1dc.com",
        # "BRSPA2ASMINT01B.1dc.com",
        # "INBOM1ASMINT01B.1dc.com",
        # "USOMA1ASMINT01B.1dc.com",
        # OFS Devices
        # "ecdbkel02-guest02",  # ERROR DEVICES
        # "ecdbkel01-guest02",  # ERROR DEVICES
        # "ecdbkel02-guest02.network.onefiserv.net",  # ERROR DEVICES
        # "ecddmzl02-guest02.network.onefiserv.net",  # ERROR DEVICES
        # "ecdbkel02.network.onefiserv.net",  # ERROR DEVICES
        # "ecdbkel01-guest02.network.onefiserv.net",  # ERROR DEVICES
        # "elidpxy03.onefiserv.net",  # ERROR DEVICES
        # "USIRT01SLBLWR01B.network.onefiserv.net",  # ERROR DEVICES
        # "ecddmzg02.fiserv.net",  # ERROR DEVICES
        # "ecddmz01-guest02.network.onefiserv.net",  # ERROR DEVICES
        # "elidpxy04.onefiserv.net",  # ERROR DEVICES
        # "jxpdapxy02.onefiserv.net",  # ERROR DEVICES
    ]
)

DISREGARD_LB_CITRIX = [
    # "INCHE1SLBINT03b",
    # "AUSYD1SLBSFM01B-D2NR",
    # "DEFRA2SLBPCF01B-SDX",
    # "AUSYD2SLBSFM01A-D2NR",
    # "ARBNA2SLBSFM01B-D2NR",
    # "USOMA1SLBINT03B",
    # "INMUM1SLBSFM01A-C2",
    # "USOMA1SLBSFA02A",
    # "ARBNA2SLBSFM01B-TESTLEG",
    # "AUSYD2SLBSFM01B-A2R",
]
