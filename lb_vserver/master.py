# pylint: disable=W1203, C0103, W0631, W0401, W0703, C0412
"""Master."""

import os
from citrix_adm.client import ADMClient
from f5_bigiq.client import BigIQClient
from helper.local_helper import log
from citrix.citrix_main import CITIRIX_MAIN
from f5.f5_main import F5_MAIN
from nautobot.nautobot_vip_delete import LB_VIP_DELETE
from helper.local_helper import get_credentials


env = os.environ.get("RD_OPTION_ENV")
# token = os.environ.get("HASHI_TOKEN")
nburl = os.environ.get("RD_OPTION_NAUTOBOT_URL")

if __name__ == "__main__":
    log.info(f"Environment {env}")
    svcp, svcu, lowu, lowp = get_credentials()
    try:
        if "Netscaler" in env:
            adm = ADMClient("https://adc.1dc.com/nitro/v1/", svcu, svcp)
            if env == "OFD_Netscaler":
                tags = ["ofd"]
            elif env == "OFS_Netscaler":
                tags = ["ofs"]
            CITIRIX_MAIN(adm, tags, env)
        elif "F5" in env:
            tags = ["ofs"]
            if env == "OFD_F5":
                f5 = BigIQClient("https://USOMA1VCDBIQ01A.1dc.com/mgmt/", svcu, svcp, "ACS-RADIUS")
                tags = ["ofd"]
            elif env == "OFS_F5":
                f5 = BigIQClient("https://jxppbigiq01.network.onefiserv.net/mgmt/", svcu, svcp, "ClearPass")
            elif env == "OFS_F5_Lower":
                f5 = BigIQClient("https://txppbigiq01.network.onefiserv.net/mgmt/", lowu, lowp, "TACACS+")
            F5_MAIN(f5, tags, env)
        elif "DELETE-ALL" in env:
            vipdel = LB_VIP_DELETE()
            vipdel.vip_delete()
    except Exception as err:
        log.error(f"{err}")
