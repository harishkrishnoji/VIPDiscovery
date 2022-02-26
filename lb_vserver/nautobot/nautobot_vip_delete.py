# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""

from helper.local_helper import log
from nautobot.nautobot_attr import VIPT_ATTR


class LB_VIP_DELETE(VIPT_ATTR):
    """Initiate VIP Delete Class."""

    def vip_delete(self):
        vips = VIPT_ATTR.vip_attr.all()
        log.info(f"Deleting VIPs [{len(vips)}]...")
        for vip in vips:
            vip.delete()
        self.pool_delete()
        self.members_delete()
        self.policies_delete()
        self.partitions_delete()
        self.environments_delete()
        self.certificates_delete()
        self.issuer_delete()
        self.organization_delete()
        log.info("Job done")

    def pool_delete(self):
        pools = VIPT_ATTR.pools_attr.all()
        log.info(f"Deleting Pools [{len(pools)}]...")
        for pool in pools:
            pool.delete()

    def members_delete(self):
        members = VIPT_ATTR.members_attr.all()
        log.info(f"Deleting Pool Members [{len(members)}]...")
        for member in members:
            member.delete()

    def policies_delete(self):
        policies = VIPT_ATTR.policies_attr.all()
        log.info(f"Deleting Policies [{len(policies)}]...")
        for policy in policies:
            policy.delete()

    def partitions_delete(self):
        partitions = VIPT_ATTR.partitions_attr.all()
        log.info(f"Deleting Partitions [{len(partitions)}]...")
        for partition in partitions:
            partition.delete()

    def certificates_delete(self):
        certificates = VIPT_ATTR.certificates_attr.all()
        log.info(f"Deleting Certificates [{len(certificates)}]...")
        for certificate in certificates:
            certificate.delete()

    def environments_delete(self):
        environments = VIPT_ATTR.environments_attr.all()
        log.info(f"Deleting Environments [{len(environments)}]...")
        for environment in environments:
            environment.delete()

    def issuer_delete(self):
        issuers = VIPT_ATTR.issuer_attr.all()
        log.info(f"Deleting Issuers [{len(issuers)}]...")
        for issuer in issuers:
            issuer.delete()

    def organization_delete(self):
        organizations = VIPT_ATTR.organization_attr.all()
        log.info(f"Deleting Organizations [{len(organizations)}]...")
        for organization in organizations:
            organization.delete()
