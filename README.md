# Zervice.ZUP Monitoring Service

<!-- Wireframe layout
|- squash.zalad.io (1 failing, 14 passing)
|  |
|  |- √   ping       50ms    40ms   30ms      (rtt to the internet)             args: {rate: 10, host: '8.8.8.8', 'count': 1}
|  |- √   dns         2ms     3ms    1ms      (time to resolve the given host)  args: {rate: 10, host: 'squash.zalad.io', match: get_public_ip()}
|  |- X   ssh        925!       4      0      (number of failed logins)         args: {rate: 60, thresholds: [[1, 3], [60, 5], [60*60, 20], [60*60*24, 50]]}
|  |- √   vpn        25ms    23ms   34ms      (time to ping grape.vpn)         
|  |- √   mem         22%    92%!    55%      (system RAM+SWAP pressure)
|  |- ...
|  |- X   argo       502!     200    200      (test https://squash.zervice.io response code via argo tunnel)
|
|- grape.zalad.io (15 passing)
|  |
|  |- √   ping        2ms     3ms    1ms      (round trip time to 1.1.1.1)
|  |- X   ssh        925!       4      0      (failed logins)
|  |- ...
| 
|- ...
-->


/opt/zervice.zup/
    etc/
        supervisor/
            zervice.zup.conf
        zup/
            config.yml
                
    data/
        zup/
            zup_db.sqlite3

            scripts/
                monadical-cloud.sh
            checks/
                monadical-cloud.yml
                    monadical_cloud:
                        test: 'scripts/monadical-cloud.sh'
                        interval: 60s
                        timeout: 30s

                    

        logs/
            zup_server.log
            zup_cron.log
            check_ping.log
            check_ssh.log
            ...


    docker-compose.yml
        flask:
            cmd: '/opt/zervice.zup/zup/server.py --config=/opt/zervice.zup/etc/zup/config.yml'
            expose:
                - 2202
            networks:
                - hera
            labels:
                hera.hostname: grape.zervice.io
                hera.port: 2202
            volumes:
                - './etc/zup:/opt/zup/etc:ro'
                - './data:/opt/zup/data'
        cron:
            cmd: '/opt/zervice.zup/zup/cron.py --config=/opt/zervice.zup/etc/zup/config.yml'
            volumes:
                - './etc/zup:/opt/zervice.zup/etc:ro'
                - './data:/opt/zervice.zup/data'

    zup/
        server.py
        cron.py
        default_checks/
