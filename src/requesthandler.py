from typing import Tuple
import network
import time
import urequests
import secrets


class RequestHandler:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)

    def get_json(self, url: str) -> Tuple[bool, str, str]:
        """
        Gets the json from a given url.
        Returns tuple with (success, status, json).
        """
        success, status = self._connect()
        if not success:
            return False, status, None

        request = urequests.get(url)
        if request.status_code != 200:
            return False, "HTTP error:" + str(request.status_code), None

        json = request.json()
        request.close()

        self._disconnect()

        return True, request.status_code, json

    def _connect(self) -> Tuple[bool, str]:
        """
        Creates a connection to the network.
        Returns status as tuple (success, status).
        """
        self._wlan.active(True)

        self._wlan.connect(secrets.SSID, secrets.PASSWORD)

        # Wait for connection
        for _ in range(15):
            if self._wlan.isconnected():
                return True, self._wlan.status()

            time.sleep(1)

        # Connection failed
        return False, "Connection error:" + str(self._wlan.status())

    def _disconnect(self):
        """
        Closes connection.
        """
        self._wlan.active(False)
