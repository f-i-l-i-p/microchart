import network
import time
import urequests
import secrets


class RequestException(Exception):
    pass


class RequestHandler:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)

    def get_json(self, url: str) -> dict:
        """
        Returns the json from a given url.
        Raises a RequestException if unsuccessful.
        """
        self._connect()

        request = urequests.get(url)
        status_code = request.status_code

        if status_code != 200:
            request.close()
            self._disconnect()
            raise RequestException("HTTP status:" + str(status_code))

        json = request.json()
        request.close()

        self._disconnect()

        return json

    def _connect(self) -> None:
        """
        Creates a connection to the network.
        """
        self._wlan.active(True)

        self._wlan.connect(secrets.SSID, secrets.PASSWORD)

        # Wait for connection
        for _ in range(15):
            if self._wlan.isconnected():
                return

            time.sleep(1)

        # Connection failed
        self._disconnect()
        raise RequestException("Could not connect to network")

    def _disconnect(self):
        """
        Closes connection.
        """
        self._wlan.active(False)
