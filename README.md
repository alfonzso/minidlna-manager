## Manage minidlna-server which is running in docker

### Main functionality: Restart minidlna server with rescan all of your media.

This app ( manager ) is a "simple" http server, which will restart minidlna-server container at a remote host or in local host.

### Example for minidlna-server:
```yaml
version: '3.3'
services:
    minidlna-server:
        network_mode: host
        restart: always
        volumes:
        - '</video/mount/path>:/media/video'
        user: "root"
        ports:
        - 8200:8200
        - 1900:1900/udp
        environment:
        - TINI_SUBREAPER=register
        - MINIDLNA_MEDIA_DIR_1=/media/video
        - MINIDLNA_FRIENDLY_NAME=RPI_MINIDLNA
        - MINIDLNA_INOTIFY=yes
        - MINIDLNA_NOTIFY_INTERVAL=120
        - MINIDLNA_PORT=8200
        - MINIDLNA_LOG_LEVEL=general,artwork,database,inotify,scanner,metadata,http,ssdp,tivo=info
        - MINIDLNA_WIDE_LINKS=yes
        image: vladgh/minidlna
```

### Dependencies:
* python3.7 >=
* pip3
* python docker lib # https://docker-py.readthedocs.io/en/stable/
### How to run/test/develope minidlna-manager

```shell
$ cd ./minidlna-server
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip3 install docker
$ python3 main.py
```

Example for run manager beside minidlna-server
```yaml
version: '3.3'
services:
    minidlna-server:
    ...

    minidlna-man:
        restart: always
        volumes:
        -  /var/run/docker.sock:/var/run/docker.sock
        ## Default values
        # - MINIDLNA_MAN_HOST=0.0.0.0
        # - MINIDLNA_MAN_PORT=1032
        # - MINIDLNA_SERVER_CONTAINER_NAME_PATTERN=minidlna-server
        ports:
        - 1032:1032
        image: minidlna-man:latest
```
Example for run manager ( almost ) anywhere <br>
! IMOPRTANT !<br>
Enable tcp connection in docker service ( ```/lib/systemd/system/docker.service``` ) with this ```-H=tcp://0.0.0.0:2375``` <br>
Example: <br>
```ExecStart=/usr/bin/dockerd -H fd:// -H=tcp://0.0.0.0:2375 --containerd=/run/containerd/containerd.sock```<br>
! IMOPRTANT !<br>
```yaml
version: '3.3'
services:
    minidlna-man:
        restart: always
        environment:
        - DOCKER_HOST=192.168.1.199:2375
        ## Default values
        # - MINIDLNA_MAN_HOST=0.0.0.0
        # - MINIDLNA_MAN_PORT=1032
        # - MINIDLNA_SERVER_CONTAINER_NAME_PATTERN=minidlna-server
        ports:
        - 1032:1032
        image: minidlna-man:latest
```

### MINIDLNA_SERVER_CONTAINER_NAME_PATTERN<br>
This 'pattern' will help to find minidlna-server container ( by name ).<br>
Example: My minidlna-server container name is "minidlna_minidlna-server_1" so my pattern will be "minidlna-server"<br>