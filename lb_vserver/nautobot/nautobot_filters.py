from random import randint


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


def cert_filter1(data, certificate):
    if (
        (data.get("serial_number") and len(data.get("serial_number")) > 10)
        and (data.get("serial_number") != certificate.serial_number)
    ):
        return True


def cert_serial(cert_data):
    if not cert_data.get("cert_serial") or cert_data.get("cert_serial") == "01":
        serial = randint(100, 2000)
    else:
        serial = cert_data.get("cert_serial")
    return {"serial": serial}
