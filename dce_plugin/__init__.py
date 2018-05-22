import base64
import json
import os
import ssl
import urllib2
import urlparse

__all__ = ['PluginSDK', 'PluginSDKException']

CONFIG_MAX_SIZE = 1024 * 1024
DCE_CONTROLLER_DB_PATH = os.getenv('DCE_MANAGER_DB_PATH') or '/var/local/dce/controller.db'

class PluginSDKException(Exception):
    pass


class PluginSDK(object):
    def __init__(self):
        pass

    def _detect_host_ip(self):
        with open(DCE_CONTROLLER_DB_PATH) as f:
            controller_ips = [l.strip() for l in f.readlines()]
        return controller_ips[0]

    def _detect_dce_ports(self):
        """
        :return: (swarm_port, controller_port, controller_ssl_port)
        """
        controller_port = os.getenv('CONTROLLER_EXPORTED_PORT') or 80
        controller_ssl_port = os.getenv('CONTROLLER_SSL_EXPORTED_PORT') or 443
        ports = int(controller_port), int(controller_ssl_port)

        return ports

    def _plugin_storage_url(self):
        storage_url = os.getenv('DCE_PLUGIN_STORAGE_URL')
        if not storage_url:
            raise PluginSDKException("Environment variable `DCE_PLUGIN_STORAGE_URL` is missed")

        host_ip = self._detect_host_ip()
        controller_port, controller_ssl_port = self._detect_dce_ports()
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
