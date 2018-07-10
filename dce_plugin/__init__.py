import base64
import json
import os
import ssl
import urllib2
import urlparse

from .docker_client import DockerClient

__all__ = ['PluginSDK', 'PluginSDKException']

CONFIG_MAX_SIZE = 1024 * 1024
DCE_CONTROLLER_DB_PATH = os.getenv('DCE_CONTROLLER_DB_PATH') or '/var/local/dce/engine/controller.db'


class PluginSDKException(Exception):
    pass


class PluginSDK(object):
    def __init__(self, base_url=None, timeout=None):
        self.docker_client = DockerClient(base_url=base_url, timeout=timeout)
        pass

    def _detect_host_ip(self):
        # DCE 2.6 - 2.10 is using docker swarmkit
        info = self.docker_client.info()
        host_ip = info.get('Swarm', {}).get('NodeAddr')
        if host_ip:
           return host_ip

        # since DCE 3.0, controller ips are save in local db file.
        try:
            with open(DCE_CONTROLLER_DB_PATH) as f:
                controller_ip = f.readline().strip()
        except IOError:
            raise PluginSDKException("Detect node address failed")
        if controller_ip:
            return controller_ip

    def _detect_dce_ports(self):
        """
        :return: (swarm_port, controller_port, controller_ssl_port)
        """
        info = self.docker_client.info()
        node_swarm_state = info.get('Swarm', {}).get('LocalNodeState')
        # for DCE 3.0, swarm is inactive
        if node_swarm_state is "inactive":
            controller_port = os.getenv('CONTROLLER_EXPORTED_PORT') or 80
            controller_ssl_port = os.getenv('CONTROLLER_SSL_EXPORTED_PORT') or 443
            return None, int(controller_port), int(controller_ssl_port)

        # DCE 2.6 - 2.10 is using docker swarmkit
        dce_base = self.docker_client.service_inspect('dce_base')
        environments = dce_base.get('Spec', {}).get('TaskTemplate', {}).get('ContainerSpec', {}).get('Env', [])
        environments = dict(
            [e.split('=', 1) for e in environments if '=' in e]
        )
        (swarm_port, controller_port, controller_ssl_port) = (
            environments.get('SWARM_PORT') or 2375,
            environments.get('CONTROLLER_PORT') or 80,
            environments.get('CONTROLLER_SSL_PORT') or 443
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
