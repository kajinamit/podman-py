import io
import json
import unittest
from types import GeneratorType

import requests_mock

from podman import PodmanClient
from podman.domain.events import EventsManager


class EventsManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.client = PodmanClient(base_url="http+unix://localhost:9999")

    def tearDown(self) -> None:
        super().tearDown()

        self.client.close()

    @requests_mock.Mocker()
    def test_list(self, mock):
        stream = [
            {
                "Type": "pod",
                "Action": "create",
                "Actor": {
                    "ID": "",
                    "Attributes": {
                        "image": "",
                        "name": "",
                        "containerExitCode": 0,
                    },
                },
                "Scope": "local",
                "Time": 1615845480,
                "TimeNano": 1615845480,
            }
        ]
        buffer = io.StringIO()
        for item in stream:
            buffer.write(json.JSONEncoder().encode(item))
            buffer.write("\n")

        adapter = mock.get(
            "http+unix://localhost:9999/v3.0.0/libpod/events", text=buffer.getvalue()
        )

        manager = EventsManager(client=self.client.api)
        actual = manager.list(decode=True)
        self.assertIsInstance(actual, GeneratorType)

        for item in actual:
            self.assertIsInstance(item, dict)
            self.assertEqual(item["Type"], "pod")

        actual = manager.list(decode=False)
        self.assertIsInstance(actual, GeneratorType)

        for item in actual:
            self.assertIsInstance(item, bytes)
            event = json.loads(item)
            self.assertEqual(event["Type"], "pod")


if __name__ == '__main__':
    unittest.main()
