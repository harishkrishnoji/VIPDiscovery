# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""


from nautobot.nautobot_attr import VIPT_ATTR


class LB_VIP_DELETE(VIPT_ATTR):
    """Initiate VIP Delete Class."""

    def vip_delete(self):
        vips = VIPT_ATTR.vip_attr.all()
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

    def pool_delete(self):
        pools = VIPT_ATTR.pools_attr.all()
        for pool in pools:
            pool.delete()

    def members_delete(self):
        members = VIPT_ATTR.members_attr.all()
        for member in members:
            member.delete()

    def policies_delete(self):
        policies = VIPT_ATTR.policies_attr.all()
        for policy in policies:
            policy.delete()

    def partitions_delete(self):
        partitions = VIPT_ATTR.partitions_attr.all()
        for partition in partitions:
            partition.delete()

    def certificates_delete(self):
        certificates = VIPT_ATTR.certificates_attr.all()
        for certificate in certificates:
            certificate.delete()

    def environments_delete(self):
        environments = VIPT_ATTR.environments_attr.all()
        for environment in environments:
            environment.delete()

    def issuer_delete(self):
        issuers = VIPT_ATTR.issuer_attr.all()
        for issuer in issuers:
            issuer.delete()

    def organization_delete(self):
        organizations = VIPT_ATTR.organization_attr.all()
        for organization in organizations:
            organization.delete()
