import functools
import httplib
import json
import os
import socket
import urlparse
from urllib import splitnport

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_DOCKER_HOST = 'unix://var/run/docker.sock'
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_UNIX_SOCKET = "http+unix://var/run/docker.sock"
DEFAULT_NPIPE = 'npipe:////./pipe/docker_engine'


class DockerException(Exception):
    """
    A base class from which all other exceptions inherit.

    If you want to catch all errors that the Docker SDK might raise,
    catch this base exception.
    """


# Based on utils.go:ParseHost http://tinyurl.com/nkahcfh
# fd:// protocol unsupported (for obvious reasons)
# Added support for http and https
# Protocol translation: tcp -> http, unix -> http+unix
def parse_host(addr, is_win32=False, tls=False):
    proto = "http+unix"
    port = None
    path = ''

    if not addr and is_win32:
        addr = DEFAULT_NPIPE

    if not addr or addr.strip() == 'unix://':
        return DEFAULT_UNIX_SOCKET

    addr = addr.strip()
    if addr.startswith('http://'):
        addr = addr.replace('http://', 'tcp://')
    if addr.startswith('http+unix://'):
        addr = addr.replace('http+unix://', 'unix://')

    if addr == 'tcp://':
        raise DockerException(
            "Invalid bind address format: {0}".format(addr)
        )
    elif addr.startswith('unix://'):
        addr = addr[7:]
    elif addr.startswith('tcp://'):
        proto = 'http{0}'.format('s' if tls else '')
        addr = addr[6:]
    elif addr.startswith('https://'):
        proto = "https"
        addr = addr[8:]
    elif addr.startswith('npipe://'):
        proto = 'npipe'
        addr = addr[8:]
    elif addr.startswith('fd://'):
        raise DockerException("fd protocol is not implemented")
    else:
        if "://" in addr:
            raise DockerException(
                "Invalid bind address protocol: {0}".format(addr)
            )
        proto = "https" if tls else "http"

    if proto in ("http", "https"):
        address_parts = addr.split('/', 1)
        host = address_parts[0]
        if len(address_parts) == 2:
            path = '/' + address_parts[1]
        host, port = splitnport(host)

        if port is None:
            raise DockerException(
                "Invalid port: {0}".format(addr)
            )

        if not host:
            host = DEFAULT_HTTP_HOST
    else:
        host = addr

    if proto in ("http", "https") and port == -1:
        raise DockerException(
            "Bind address needs a port: {0}".format(addr))

    if proto == "http+unix" or proto == 'npipe':
        return "{0}://{1}".format(proto, host).rstrip('/')
    return "{0}://{1}:{2}{3}".format(proto, host, port, path).rstrip('/')


class UnixHTTPConnection(httplib.HTTPConnection):
    def __init__(self, socket_path, host=None, port=None, strict=None, timeout=None):
        host = host or 'localhost'
        httplib.HTTPConnection.__init__(self, host, port=port, strict=strict, timeout=timeout)
        self.socket_path = socket_path

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.socket_path)
        sock.settimeout(self.timeout)
        self.sock = sock


class DockerClient(object):
    @staticmethod
    def docker_host_from_env():
        return os.getenv('DOCKER_HOST') or DEFAULT_DOCKER_HOST

    def __init__(self, base_url=None, timeout=DEFAULT_TIMEOUT_SECONDS):
        super(DockerClient, self).__init__()

        base_url = base_url or self.docker_host_from_env()
        self.base_url = parse_host(base_url)

        if self.base_url.startswith('http+unix://'):
            socket_path = self.base_url.replace('http+unix://', '')
            if not socket_path.startswith('/'):
                socket_path = '/' + socket_path

            self.conn_fac = functools.partial(UnixHTTPConnection, socket_path, timeout=timeout)
        elif self.base_url.startswith('http://'):
            _, netloc, _, _, _, _ = urlparse.urlparse(self.base_url)
            host, port = netloc.split(':')
            self.conn_fac = functools.partial(httplib.HTTPConnection, host, port=port, timeout=timeout)
        else:
            raise DockerException(
                "Invalid docker host: {}".format(self.base_url)
            )

    def _request(self, method, path, as_json=True, **kwargs):
        conn = self.conn_fac()
        conn.request(method, path)
        resp = conn.getresponse()
        data = resp.read()
        if as_json:
            data = json.loads(data)
        return data

    def info(self):
        info = self._request('GET', '/info')
        return info

    def service_inspect(self, service):
        path = '/services/{}'.format(service)
        service = self._request('GET', path)
        return service
