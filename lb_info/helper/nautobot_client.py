"""Nautobot REST API SDK."""

import requests
from requests.compat import urljoin
import json
import sys
from helper.script_conf import LOG

requests.packages.urllib3.disable_warnings()


class NautobotClient:
    """Create a Nautobot API client."""

    def __init__(self, url=None, token=None, ssl_verify=False):
        """Initialize the Nautobot API client.

        Args:
            url (str): Nautobot API URL (ending with: /api/').
            toke (str): Authorization token for Nautobot API.
            ssl_verify (bool): Whether or not to verify SSL certificate.
        """
        if "/api/" not in url:
            raise ValueError(f"{url} must include /api/")
        self.url = url
        self.ssl_verify = ssl_verify
        self.token = token
        self.session = requests.Session()
        self.sid = None
        self.log = LOG("nautobot_client")

    def _request(self, method, path, **kwargs):
        """Return a response object after making a request that can be parsed by other methods.

        Args:
            method (str): Request method to call in self.session.
            path (str): URL path to call.

        Returns:
            Requests response object.
        """

        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {self.token}",
        }

        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = headers
        kwargs.setdefault("verify", self.ssl_verify)
        url = urljoin(self.url, path)
        if kwargs.get("data"):
            kwargs["data"] = json.dumps(kwargs["data"])
        resp = self.session.request(method, url, **kwargs)
        self.log.debug(resp.status_code)
        try:
            resp.raise_for_status()
        except Exception as err:
            sys.exit(f"Error with connectivity to url - {self.url} : {err}")
        return resp

    def show_vip(self):
        """Retrieve all VIP.

        Returns:
            :class:`~requests.Response`: Response from the API.
        """
        kwargs = {}
        return self._request("get", "plugins/vip-tracker/vip/", **kwargs)

    def nb_data(self, method, uri, **kwargs):
        """Returns the details of a specified url.

        Args:
            method (str): GET, POST, PATCH.
            uri (str): URI path to pull data.
            kwargs (dict): Payload data for url.

        Returns:
            :class:`~requests.Response`: Response from the API.
        """
        return self._request(method, uri, **kwargs)
