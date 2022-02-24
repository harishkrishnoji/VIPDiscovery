from helper.variables_lb import DISREGARD_LB_F5, F5_STANDALONE, F5_DEVICE_TO_QUERY, DISREGARD_VIP, FILTER_VIP

# F5_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")


def filter_device(device):
    # For Test or Troubleshooting purpose
    # Filter the devices for which you want to discover VIPs
    if "All" in F5_DEVICE_TO_QUERY or device["hostname"] in F5_DEVICE_TO_QUERY:
        return True


def filter_device1(item):
    for i in enumerate(DISREGARD_LB_F5):
        if DISREGARD_LB_F5[i[0]] in item["hostname"]:
            return True


def filter_standalone(item):
    for i in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i[0]] in item["hostname"]:
            return True


def filter_vips(addr, vip):
    if addr not in DISREGARD_VIP and vip.get("pool") and ("All" in FILTER_VIP or vip.get("name") in FILTER_VIP):
        return True
