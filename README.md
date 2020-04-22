# Zervice.ZUP Monitoring Service

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
