import os
from citrix_adm.client import ADMClient
from f5_bigiq.client import BigIQClient
from helper.nautobot_client import NautobotClient
from helper.script_conf import *
from master_citrix import citrix_master
from master_f5 import f5_master

log = LOG("master")
log.info("Initiated")

ENV = os.environ.get("RD_OPTION_ENV")
svcp = os.environ.get("RD_OPTION_SVC_PWD")
svcu = os.environ.get("RD_OPTION_SVC_USER")
lowu = os.environ.get("RD_OPTION_LOWER_USER")
lowp = os.environ.get("RD_OPTION_LOWER_PWD")
npwd = os.environ.get("RD_OPTION_NAUTOBOT_KEY")

NB = NautobotClient("https://nautobot.onefiserv.net/api/", npwd)

if __name__ == "__main__":

    if ENV == "OFD_Netscaler":
        adm = ADMClient("https://adc.1dc.com/nitro/v1/", svcu, svcp)
        citrix_master(adm, NB, ENV)
    elif ENV == "OFD_F5":
        f5 = BigIQClient("https://10.165.232.72/mgmt/", svcu, svcp, "ACS-RADIUS")
        f5_master(f5, NB, ENV)
    elif ENV == "OFS_F5":
        f5 = BigIQClient("https://10.224.134.85/mgmt/", svcu, svcp, "ClearPass")
        f5_master(f5, NB, ENV)
    elif ENV == "OFS_F5_Lower":
        f5 = BigIQClient("https://10.224.134.85/mgmt/", lowu, lowp, "TACACS+")
        f5_master(f5, NB, ENV)
    elif ENV == "OFS_Netscaler":
        adm = ADMClient("https://adc.1dc.com/nitro/v1/", svcu, svcp)
        citrix_master(adm, NB, ENV)
