# pylint: disable=W1203, C0103, W0631, W0401, W0703, C0412
"""Master."""

import os
from citrix_adm.client import ADMClient
from f5_bigiq.client import BigIQClient
from helper.local_helper import log
from citrix.citrix_master import citrix_master
from f5.f5_master import f5_master

ENV = os.environ.get("RD_OPTION_ENV")
svcp = os.environ.get("RD_OPTION_SVC_PWD")
svcu = os.environ.get("RD_OPTION_SVC_USER")
lowu = os.environ.get("RD_OPTION_LOWER_USER")
lowp = os.environ.get("RD_OPTION_LOWER_PWD")

log.debug("Master Initiated.. ")
log.info(f"Environment {ENV}")

if __name__ == "__main__":
    try:
        if "Netscaler" in ENV:
            adm = ADMClient("https://adc.1dc.com/nitro/v1/", svcu, svcp)
            if ENV == "OFD_Netscaler":
                tags = ["ofd", "netscaler"]
            elif ENV == "OFS_Netscaler":
                tags = ["ofs", "netscaler"]
            citrix_master(adm, tags, ENV)
        elif "F5" in ENV:
            if ENV == "OFD_F5":
                f5 = BigIQClient("https://10.165.232.72/mgmt/", svcu, svcp, "ACS-RADIUS")
                tags = ["ofd", "f5"]
            elif ENV == "OFS_F5":
                f5 = BigIQClient("https://11.224.134.85/mgmt/", svcu, svcp, "ClearPass")
                tags = ["ofs", "f5"]
            elif ENV == "OFS_F5_Lower":
                f5 = BigIQClient("https://11.35.169.85/mgmt/", lowu, lowp, "TACACS+")
                tags = ["ofs", "f5", "lowers"]
            f5_master(f5, tags, ENV)
    except Exception as err:
        log.error(f"{err}")
