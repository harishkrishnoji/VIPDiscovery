# pylint: disable=W1203, C0103, W0631
"""Script local config."""

#########################################################################
#   Mandatory keys/value required to create VIP in Nautobot
#########################################################################

VIP_FIELDS = list(["address", "port", "loadbalancer", "name"])

#########################################################################
#   List of Devices to pull data from BIG-IQ / ADM Netscaler
#########################################################################

F5_DEVICE_TO_QUERY = list(["ltm1.opensolutionsasp.com"])
# F5_DEVICE_TO_QUERY = list(["lv-f5core-02.fiservip.net"])
NS_DEVICE_TO_QUERY = list(["All"])
FILTER_VIP = list(["All"])
# FILTER_VIP = list(["chh-dna-1206v-s"])

#########################################################################
#   List of Keys/values which need to be collected from BIG-IQ / ADM Netscaler
#########################################################################

F5_DEVICE_FIELDS = list(["uuid", "address", "product", "version", "hostname", "platformMarketingName"])
NS_DEVICE_FIELDS = list(
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
#   F5 Standalone devices
#########################################################################

F5_STANDALONE = list(["SLBAPP1", "OMA1GIOF5A"])

#########################################################################
#   List of VIPs which need to be disregarded from F5 devices
#########################################################################

DISREGARD_VIP = list(
    ["0.0.0.0", "1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5", "255.255.255.255", "255.255.255.254", ":0"]
)

#########################################################################
#   List of LB instances to disregard from BIG-IQ / ADM Netscaler
#########################################################################

DISREGARD_LB_F5 = list(
    [
        # OFD Devices
        "slbfde",  # FDE Instances
        "DEFRA1VCDDFA01A-GTM.1dc.com",  # EMEA GTM
        "DEFRA1VCDDFA01B-GTM.1dc.com",  # EMEA GTM
        "DEFRA2VCDDFA01A-GTM.1dc.com",  # EMEA GTM
        "DEFRA2VCDDFA01B-GTM.1dc.com",  # EMEA GTM
        "USOMA1VCDDFA01A-GTM.1dc.com",  # NA GTM
        "USOMA1VCDDFA01B-GTM.1dc.com",  # NA GTM
        "USCHD1VCDDFA01A-GTM.1dc.com",  # NA GTM
        "USCHD1VCDDFA01B-GTM.1dc.com",  # NA GTM
        "OMA1GIOF5B-v1.giolab.local",
        "SLBAPP2",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "SLBAPP3",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "SLBAPP1",  # Cluster mode SLBAPP1, SLBAPP2, SLBAPP2
        "localhost",
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
