import base64
import json
import os
import ssl
import urllib2
import urlparse

from .docker_client import DockerClient
from .docker_client import DockerException

__all__ = ['PluginSDK', 'PluginSDKException']

CONFIG_MAX_SIZE = 1024 * 1024


class PluginSDKException(Exception):
    pass


class PluginSDK(object):
    def __init__(self, base_url=None, timeout=None):
        self.docker_client = DockerClient(base_url=base_url, timeout=timeout)

    def _detect_host_ip(self):
        info = self.docker_client.info()
        host_ip = info.get('Swarm', {}).get('NodeAddr')
        if not host_ip:
            raise PluginSDKException("Detect node address failed")

        return host_ip

    def _detect_dce_ports(self):
        """
        :return: (swarm_port, controller_port, controller_ssl_port)
        """
        dce_base = self.docker_client.service_inspect('dce_base')
        environments = dce_base.get('Spec', {}).get('TaskTemplate', {}).get('ContainerSpec', {}).get('Env', [])
        environments = dict(
            [e.split('=', 1) for e in environments if '=' in e]
        )
        (swarm_port, controller_port, controller_ssl_port) = (
            environments.get('SWARM_PORT'),
            environments.get('CONTROLLER_PORT'),
            environments.get('CONTROLLER_SSL_PORT')
        )
        if not (swarm_port and controller_port and controller_ssl_port):
            raise PluginSDKException("Detect DCE ports failed")

        ports = int(swarm_port), int(controller_port), int(controller_ssl_port)

        return ports

    def _plugin_storage_url(self):
        storage_url = os.getenv('DCE_PLUGIN_STORAGE_URL')
        if not storage_url:
            raise PluginSDKException("Environment variable `DCE_PLUGIN_STORAGE_URL` is missed")

        host_ip = self._detect_host_ip()
        _, controller_port, controller_ssl_port = self._detect_dce_ports()
        config = {
            'DCE_HOST': host_ip,
            'DCE_PORT': controller_ssl_port
        }
        if storage_url.startswith('http://'):
            config['DCE_PORT'] = controller_port

        return storage_url.format(**config)

    def _build_request(self, method, url, data=None):
        parts = urlparse.urlparse(url)

        safe_parts = parts._replace(netloc='{}:{}'.format(parts.hostname, parts.port))
        safe_url = safe_parts.geturl()
        auth = base64.urlsafe_b64encode('{}:{}'.format(parts.username, parts.password))

        req = urllib2.Request(safe_url, data=data)
        req.add_header('Authorization', 'Basic {}'.format(auth))
        req.add_header('Content-Type', 'application/json')
        req.get_method = lambda: method
        return req

    def set_config(self, config):
        data = json.dumps(config)
        if len(data) > CONFIG_MAX_SIZE:
            raise PluginSDKException("config should not bigger than 1MB")

        storage_url = self._plugin_storage_url()
        response = urllib2.urlopen(
            self._build_request('PUT', storage_url, data),
            context=ssl._create_unverified_context()
        )
        return json.load(response)

    def get_config(self):
        storage_url = self._plugin_storage_url()
        response = urllib2.urlopen(
            self._build_request('GET', storage_url),
            context=ssl._create_unverified_context()
        )
        return json.load(response)
