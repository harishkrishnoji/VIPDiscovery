from deepdiff import DeepDiff

odata = [
    {
        "address": "10.98.50.10",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "AFIP-PROD",
        "pool": "SRVG-AFIP-PROD",
        "pool_mem": [
            "10.98.20.21",
            "10.98.20.22"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.14",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD-BBVA-TEST",
        "pool": "SRVG-CENCOSUD-BBVA-TEST",
        "pool_mem": [
            "10.98.20.36",
            "10.98.20.37"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.15",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD-BBVA-PROD",
        "pool": "SRVG-CENCOSUD-BBVA-PROD",
        "pool_mem": [
            "10.98.20.38",
            "10.98.20.39"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.13",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-PROD",
        "pool": "SRVG-PAYMENT-FACILITATOR-PROD",
        "pool_mem": [
            "10.98.20.34",
            "10.98.20.35"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.11",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-DEV",
        "pool": "SRVG-PAYMENT-FACILITATOR-DEV",
        "pool_mem": [
            "10.98.20.30",
            "10.98.20.31"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.12",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-TEST",
        "pool": "SRVG-PAYMENT-FACILITATOR-TEST",
        "pool_mem": [
            "10.98.20.32",
            "10.98.20.33"
        ],
        "port": 8443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.16",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "DRPOSNET",
        "pool": "SRVG-DRPOSNET",
        "pool_mem": [
            "10.98.20.41",
            "10.98.20.42"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.16",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "DRPOSNET80",
        "pool": "SRVG-DRPOSNET80",
        "pool_mem": [
            "10.98.20.41",
            "10.98.20.42"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.17",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "FDARGENTINA",
        "pool": "SRVG-FDARGENTINA",
        "pool_mem": [
            "10.98.20.43",
            "10.98.20.44"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.18",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "FDURUGUAY",
        "pool": "SRVG-FDURUGUAY",
        "pool_mem": [
            "10.98.20.47",
            "10.98.20.48"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.23",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PORTALATENCION-443",
        "pool": "SRVG-PORTALATENCION-443",
        "pool_mem": [
            "10.98.20.58",
            "10.98.20.59"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.23",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PORTALATENCION-80",
        "pool": "SRVG-PORTALATENCION-80",
        "pool_mem": [
            "10.98.20.58",
            "10.98.20.59"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.20",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "BC-PREPAID-WEB",
        "pool": "SRVG-BC-PREPAID-WEB",
        "pool_mem": [
            "10.98.20.45",
            "10.98.20.46"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.21",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD_SGR_TEST",
        "pool": "SRVG-CENCOSUD_SGR_TEST",
        "pool_mem": [
            "10.98.20.54",
            "10.98.20.55"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    }
]

ndata = [
    {
        "address": "10.98.50.10",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "AFIP-PROD",
        "pool": "SRVG-AFIP-PROD",
        "pool_mem": [
            "10.98.20.21",
            "10.98.20.22"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.14",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD-BBVA-TEST",
        "pool": "SRVG-CENCOSUD-BBVA-TEST",
        "pool_mem": [
            "10.98.20.36",
            "10.98.20.37"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.15",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD-BBVA-PROD",
        "pool": "SRVG-CENCOSUD-BBVA-PROD",
        "pool_mem": [
            "10.98.20.38",
            "10.98.20.39"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.13",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-PROD",
        "pool": "SRVG-PAYMENT-FACILITATOR-PROD",
        "pool_mem": [
            "10.98.20.34",
            "10.98.20.35"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.11",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-DEV",
        "pool": "SRVG-PAYMENT-FACILITATOR-DEV",
        "pool_mem": [
            "10.98.20.30",
            "10.98.20.31"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.12",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PAYMENT-FACILITATOR-TEST",
        "pool": "SRVG-PAYMENT-FACILITATOR-TEST",
        "pool_mem": [
            "10.98.20.32",
            "10.98.20.33"
        ],
        "port": 8443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.16",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "DRPOSNET",
        "pool": "SRVG-DRPOSNET",
        "pool_mem": [
            "10.98.20.41",
            "10.98.20.42"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.16",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "DRPOSNET80",
        "pool": "SRVG-DRPOSNET80",
        "pool_mem": [
            "10.98.20.41",
            "10.98.20.42"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.17",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "FDARGENTINA",
        "pool": "SRVG-FDARGENTINA",
        "pool_mem": [
            "10.98.20.43",
            "10.98.20.44"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.18",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "FDURUGUAY",
        "pool": "SRVG-FDURUGUAY",
        "pool_mem": [
            "10.98.20.47",
            "10.98.20.48"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.23",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PORTALATENCION-443",
        "pool": "SRVG-PORTALATENCION-443",
        "pool_mem": [
            "10.98.20.58",
            "10.98.20.59"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.23",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "PORTALATENCION-80",
        "pool": "SRVG-PORTALATENCION-80",
        "pool_mem": [
            "10.98.20.58",
            "10.98.20.59"
        ],
        "port": 80,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.20",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "BC-PREPAID-WEB",
        "pool": "SRVG-BC-PREPAID-WEB",
        "pool_mem": [
            "10.98.20.45",
            "10.98.20.46"
        ],
        "port": 443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.21",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD_SGR_TEST",
        "pool": "SRVG-CENCOSUD_SGR_TEST",
        "pool_mem": [
            "10.98.20.56",
            "10.98.20.55"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    },
    {
        "address": "10.98.50.212",
        "environment": "OFD_Netscaler",
        "loadbalancer": "ARBNA1SLBSFM01A-W1R",
        "name": "CENCOSUD_SGR_TEST",
        "pool": "SRVG-CENCOSUD_SGR_TEST",
        "pool_mem": [
            "10.98.20.56",
            "10.98.20.55"
        ],
        "port": 4443,
        "protocol": "TCP",
        "tags": [
            "ofd"
        ]
    }
]

for nd in ndata:
    ndv = False
    for od in odata:
        if (
            (od.get("port") == nd.get("port")) and od.get("protocol") == nd.get("protocol")
            and (od.get("address") == nd.get("address")) and (od.get("name") == nd.get("name"))
            and (od.get("pool") == nd.get("pool")) and (od.get("environment") == nd.get("environment"))
        ):
            ndv = True
            dd = DeepDiff(od, nd, ignore_order=True, exclude_paths=["root['loadbalancer']"])
            # print(dd)
            if dd:
                print("Change in existing data")
                print(nd)
                print(dd)
    if not ndv:
        print("New data")
        print(nd)
