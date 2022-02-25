def cert_filter(cert, vip):
    if (
        cert.get("cert_serial")
        and len(cert.get("cert_serial")) > 30
        and cert.get("cert_serial") not in str(vip.get("certificates"))
    ):
        return True


def vip_port_filter(vip, vip_data):
    if (
        (vip_data.get("port") == str(vip.get("port")) and vip_data.get("protocol") == vip.get("protocol"))
        and (vip_data.get("pool_mem"))
    ):
        return True
