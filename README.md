# Zervice.ZUP Simple Monitoring Service

<img src="https://i.imgur.com/L8dvWpm.png">

## Usage
```bash
git clone https://github.com/Monadical-SAS/zervice.zup
nano zup.conf
pip install django
./monitor.py runserver 0.0.0.0:8080
open http://127.0.0.1:8080/tasks
```

Or use docker-compose:
```bash
git clone https://github.com/Monadical-SAS/zervice.zup
nano zup.conf
docker-compose up
```

## Configuration

**`zup.conf`:**
```ini
[server]
http_listen_host: *
http_listen_port: 5000
static_dir: static
template_dir: templates

[cron]
daemonize: false
processes: 4
threads: 5
default_interval: 120s
default_timeout: 15s

[includes]
files: zup/default_checks/*.conf data/zup/checks/*.conf data/zup/hosts/*.conf

...

[task:CPU Usage]
enabled: true
description: CPU pct used
cmd: uptime
    | sed 's/.*: //'
    | sed 's/, / /g'
    | awk -v CORES=$(nproc) '{{print ($1/CORES)*100}}'
validate: float(stdout) <= int(threshold)
format: {int(float(stdout))}%
returncode: 0
threshold: 75

...

[task:DNS Loopback]
enabled: false
description: DNS lookup latency for a given host + response
cmd: dig -4 +short @{nameserver} {record} {record_type}
    | grep -E '[0-9]+\.[0-9]+'
nameserver: 1.1.1.1
record: squash.zalad.io
record_type: A
returncode: 0
threshold: 200
validate: stdout == run("dig -4 +short @resolver1.opendns.com myip.opendns.com A | grep -E '[0-9]+\.[0-9]+'", shell=True, capture_output=True).stdout.decode().strip() and stdout.count(".") == 3 and (duration.total_seconds() <= int(threshold))
format: {duration.total_seconds() * 1000:.2f}ms
interval: 20s
timeout: 5s
```

## Project Layout
```
/opt/zervice.zup/
    monitor.py
    templates/
        index.html
        tasks.html
    static/
        ...
    etc/
        supervisor/
            zervice.zup.conf
        zup/
            zup.conf
                
    data/
        logs/
            zup_server.log
            zup_cron.log
            check_ping.log
            check_ssh.log
            ...
```

See more:

- https://github.com/francescou/docker-compose-ui
- https://cockpit-project.org/
- https://doxfer.webmin.com/Webmin/System_and_Server_Status
