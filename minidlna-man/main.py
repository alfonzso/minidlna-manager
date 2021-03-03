from docker.models.containers import Container
import docker
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

# import jinja2

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


def get_content_len(path):
    return str(os.path.getsize(path))


class MyServer(BaseHTTPRequestHandler):
    _paths = {
        "_index_html": None,
        "_404_html": None,
        "_javascript": None
    }
    # _path_of_index_html = None
    # # _javascript_as_string = None
    # _404_html = None
    # _javascript = None
    # _url = {"URL": "http://pi.local.net:1032/restart"}
    # _url = {"URL": "/restart"}

    class Employee(object):
        def __init__(self, _dict):
            self.__dict__.update(_dict)

    def init(self):
        root.info("__init__")
        cwd = os.path.dirname(os.path.realpath(__file__))
        # self._path_of.get('')
        self._path_of = self.Employee(self._paths)

        self._path_of._index_html = f"{cwd}/res/html/index.html"
        self._path_of._404_html = f"{cwd}/res/html/404.html"
        self._path_of._javascript = f"{cwd}/res/js/main.js"

        # templateLoader = jinja2.FileSystemLoader(searchpath="/")
        # templateEnv = jinja2.Environment(loader=templateLoader)
        # template = templateEnv.get_template(self._javascript)
        # self._javascript_as_string = template.render(self._url)

    @staticmethod
    def docker():
        client = docker.from_env()
        docker_ps = client.containers.list()
        docker_cli_minidlna: Container = [cont for cont in docker_ps if minidlna_server_container_name_pattern in cont.name][0]
        docker_cli_minidlna.exec_run("/bin/bash -c \" minidlna -R \" ")
        res = docker_cli_minidlna.exec_run("/bin/bash -c \" /usr/sbin/minidlnad -R \" ")
        docker_cli_minidlna.restart()
        # import time
        # time.sleep(2)
        # res = ""
        return f"{res} - {docker_cli_minidlna.status}"

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
