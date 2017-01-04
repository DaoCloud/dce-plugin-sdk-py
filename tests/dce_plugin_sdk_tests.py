import unittest

from dce_plugin import DockerClient
from dce_plugin import PluginSDK


class PluginSDKTest(unittest.TestCase):
    def test_client(self):
        docker_hosts = [
            'unix://var/run/docker.sock',
            'tcp://0.0.0.0:2370',
            'tcp://192.168.1.137:2370',
            'http://192.168.1.137:2370',
            'http+unix://var/run/docker.sock',
        ]

        for dh in docker_hosts:
            DockerClient(base_url=dh)

    def test_info(self):
        docker_hosts = [
            'tcp://192.168.1.137:2370',
            'unix://var/run/docker.sock'
        ]
        for dh in docker_hosts:
            c = DockerClient(base_url=dh, timeout=5)
            self.assertIsNotNone(c.info())

    def test_service_inspect(self):
        docker_host = 'tcp://192.168.1.137:2370'
        c = DockerClient(base_url=docker_host, timeout=5)
        self.assertIsNotNone(c.service_inspect('dce_base'))

    def test_detect_dce_info(self):
        docker_host = 'tcp://192.168.1.137:2370'
        sdk = PluginSDK(base_url=docker_host, timeout=5)
        self.assertEqual('192.168.1.137', sdk._detect_host_ip())
        self.assertEqual((2375, 80, 443), sdk._detect_dce_ports())

    def test_set_config(self):
        docker_host = 'tcp://192.168.1.137:2370'
        sdk = PluginSDK(base_url=docker_host, timeout=5)
        config = {
            'a': 1,
            'b': [1, 2, 3, 4, 5],
            'c': '5454',
            'd': {
                '1': 3,
                'b': [1, 2, 3, 4, 5],
            }
        }
        self.assertEqual(config, sdk.set_config(config))
        self.assertEqual(config, sdk.get_config())
