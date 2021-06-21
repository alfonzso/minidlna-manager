from docker.models.containers import Container
import docker
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

import json
import logging
import sys
import os

root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
ch.setLevel(logging.DEBUG)
root.addHandler(ch)

host_name = os.getenv("MINIDLNA_MAN_HOST", "0.0.0.0")
host_port = os.getenv("MINIDLNA_MAN_PORT", 1032)
minidlna_server_container_name_pattern = os.getenv("MINIDLNA_SERVER_CONTAINER_NAME_PATTERN", "minidlna-server")

# volumes
minidlna_volume_enabled = bool(os.getenv("MINIDLNA_VOLUME_ENABLED", False))


if minidlna_volume_enabled:
    minidlna_volume_name = os.getenv("MINIDLNA_VOLUME_NAME", "transmission-data")
    minidlna_volume_type = os.getenv("MINIDLNA_VOLUME_TYPE", "nfs")
    minidlna_volume_addr = os.getenv("MINIDLNA_VOLUME_ADDR")
    if minidlna_volume_addr is None:
        sys.exit("MINIDLNA_VOLUME_ADDR missing ! Terminating ... ")
    minidlna_volume_opts = os.getenv("MINIDLNA_VOLUME_OPTS", f'nfsvers=4,addr={minidlna_volume_addr},nfsvers=4,nolock,soft')
    minidlna_volume_device = os.getenv("MINIDLNA_VOLUME_OPTS", ':/mnt/hdd/transmission-workspace/downloads/complete/')

def get_content_len(path):
    return str(os.path.getsize(path))


class MyServer(BaseHTTPRequestHandler):
    _paths = {
        "_index_html": None,
        "_404_html": None,
        "_javascript": None
    }

    class Employee(object):
        def __init__(self, _dict):
            self.__dict__.update(_dict)

    def init(self):
        root.info("__init__")
        cwd = os.path.dirname(os.path.realpath(__file__))
        self._path_of = self.Employee(self._paths)

        self._path_of._index_html = f"{cwd}/res/html/index.html"
        self._path_of._404_html = f"{cwd}/res/html/404.html"
        self._path_of._javascript = f"{cwd}/res/js/main.js"

    @staticmethod
    def docker():
        client = docker.from_env()

        containers = [cont for cont in client.containers.list() if minidlna_server_container_name_pattern in cont.name]
        dcli_minidlna: Container = containers[0] if len(containers) > 0 else None

        if dcli_minidlna:
            dcli_stop = dcli_minidlna.remove(v=True, force=True)
        else:
            if minidlna_volume_enabled:
                vols = [vol for vol in client.volumes.list() if minidlna_volume_name in vol.name]
                if len(vols) > 0:
                    client.volumes.get(minidlna_volume_name).remove(force=True)

        vols_dict = {}
        if minidlna_volume_enabled:
            create_vol = client.volumes.create(
                name=minidlna_volume_name, driver='local',
                # driver_opts={
                #     'type': 'nfs',
                #     'o': 'nfsvers=4,addr=192.168.1.121,nfsvers=4,nolock,soft',
                #     'device': ':/mnt/hdd/transmission-workspace/downloads/complete/'
                # },
                driver_opts={
                    'type': minidlna_volume_type,
                    'o': minidlna_volume_opts,
                    'device': minidlna_volume_device
                }
            )

            vols_dict = {
                "volumes": {
                    minidlna_volume_name: {'bind': '/media/video', 'mode': 'rw'}
                }
            }

        # tst = vols_dict if minidlna_volume_enabled else {}
        # tst = vols_dict
        minidlna_srvr = client.containers.run(
            image="vladgh/minidlna",
            detach=True,
            name=minidlna_server_container_name_pattern,
            user="root",
            restart_policy={"Name": "always"},
            network_mode="host",
            **vols_dict,
            environment=[
                "TINI_SUBREAPER=register",
                "MINIDLNA_MEDIA_DIR_1=/media/video",
                "MINIDLNA_FRIENDLY_NAME=RPI_MINIDLNA",
                "MINIDLNA_INOTIFY=yes",
                "MINIDLNA_NOTIFY_INTERVAL=120",
                "MINIDLNA_PORT=8200",
                "MINIDLNA_LOG_LEVEL=general,artwork,database,inotify,scanner,metadata,http,ssdp,tivo=info",
                "MINIDLNA_WIDE_LINKS=yes",
            ],
        )

        return f"srvr stat - {minidlna_srvr.status}"

    def do_GET(self):
        self.init()
        # root.info(" -> path: %s <- " % self.path)
        if "test" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-debug", self.path)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # self.docker()
            self.wfile.write(bytes(json.dumps({'received': 'ok', 'test': "ok"}), "utf-8"))

        elif "restart" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-debug", self.path)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            root.info("before call")
            _json = json.dumps({'received': 'ok', 'status_after_restart': self.docker()})
            root.info("after call")
            self.wfile.write(bytes(_json, "utf-8"))

        elif "/res/js/main.js" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/javascript")
            self.send_header("X-debug", self.path)
            self.send_header("Content-Length", get_content_len(self._path_of._javascript))
            self.end_headers()
            # self._path_of._javascript
            # self.wfile.write(self._javascript_as_string.encode("UTF-8"))
            with open(self._path_of._javascript, 'rb') as f:
                self.wfile.write(f.read())

        elif "/" == self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header("Content-Length", get_content_len(self._path_of._index_html))
            self.end_headers()
            with open(self._path_of._index_html, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header("Content-Length", get_content_len(self._path_of._404_html))
            self.end_headers()
            with open(self._path_of._404_html, 'rb') as f:
                self.wfile.write(f.read())


myServer = HTTPServer((host_name, host_port), MyServer)
root.info("Server Starts - %s:%s" % (host_name, host_port))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
root.info("Server Stops - %s:%s" % (host_name, host_port))
