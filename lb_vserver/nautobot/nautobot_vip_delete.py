# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""


from nautobot.nautobot_attr import VIPT_ATTR


class LB_VIP_DELETE(VIPT_ATTR):
    """Initiate VIP Delete Class."""

    def vip_delete(self):
        for vip in VIPT_ATTR.vip_attr.all():
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
        for pool in VIPT_ATTR.pools_attr.all():
            pool.delete()

    def members_delete(self):
        for member in VIPT_ATTR.members_attr.all():
            member.delete()

    def policies_delete(self):
        for policy in VIPT_ATTR.policies_attr.all():
            policy.delete()

    def partitions_delete(self):
        for partition in VIPT_ATTR.partitions_attr.all():
            partition.delete()

    def certificates_delete(self):
        for certificate in VIPT_ATTR.certificates_attr.all():
            certificate.delete()

    def environments_delete(self):
        for environment in VIPT_ATTR.environments_attr.all():
            environment.delete()

    def issuer_delete(self):
        for issuer in VIPT_ATTR.issuer_attr.all():
            issuer.delete()

    def organization_delete(self):
        for organization in VIPT_ATTR.organization_attr.all():
            organization.delete()
