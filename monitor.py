#!/usr/bin/env python3
"""
./monitor.py cron &
./monitor.py server
"""

from time import sleep
from datetime import datetime, timedelta
from subprocess import run

import signal
import configparser

class timed:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        try:
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)
        except ValueError:
            pass

    def __exit__(self, type, value, traceback):
        try:
            signal.alarm(0)
        except ValueError:
            pass

class AttributeDict(dict):
    """Helper to allow accessing dict values via Example.key or Example['key']"""

    def __getattr__(self, attr: str):
        return dict.__getitem__(self, attr)

    def __setattr__(self, attr: str, value) -> None:
        return dict.__setitem__(self, attr, value)


def load_config(config_path: str):
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)

    return AttributeDict({
        'cron': config['cron'],
        'server': config['server'],
        'includes': config['includes'],
        'hosts': {
            section.replace('host:', ''): config[section]
            for section in config.sections()
            if section.startswith('host:')
        },
        'tasks': {
            section.replace('task:', ''): config[section]
            for section in config.sections()
            if section.startswith('task:')
        },
    })

CONFIG = load_config(config_path='./zup.conf')


def cron(config):
    for task_name, task in config.tasks:
        result = run_task(**task)
        with open(logs_dir / f'{task_name}.log', 'a+') as f:
            f.write(json.dumps(result))

        sleep(1)

def build_cmd(cmd, args):
    if isinstance(cmd, str):
        return cmd.replace('\n', ' ').format(**args)
    elif isinstance(cmd, (list, tuple)):
        return [
            str(section).replace('\n', ' ').format(**args)
            for section in cmd
        ]
    else:
        raise TypeError('cmd must be a str or list of strs')

def run_task(cmd, validate='duration.total_seconds() < timeout', timeout=60, interval=120, description=None, **kwargs):
    """
    description: "Redis ping latency"
    cmd: "redis-cli -h {host} ping"
    host: '127.0.0.1'
    threshold: 100
    validate: 'stdout == "PONG" and duration < threshold'
    format: '{duration.milliseconds}ms'
    timeout: 10
    interval: 30
    """
    CMD = build_cmd(cmd, kwargs)
    print()
    print(CMD.replace("\n", " "))
    start_time = datetime.now()
    exception = None
    try:
        with timed(seconds=timeout, error_message=f'Timed out after {timeout}sec'):
            proc = run(CMD, shell=True, capture_output=True)
        returncode = proc.returncode
        stdout = proc.stdout.decode().strip()
        stderr = proc.stderr.decode().strip()
    except Exception as e:
        returncode, stdout, stderr, exception = -1, '', '', e

    end_time = datetime.now()
    duration = end_time - start_time

    # check for any python exceptions during task execution
    python_passing = exception is None

    # check for any timeouts during task execution
    duration_passing = not isinstance(exception, TimeoutError)

    # check return code if returncode is specified
    expected_returncode = int(kwargs.get('returncode', 0))
    if expected_returncode == -1:
        returncode_passing = True
    else:
        returncode_passing = (returncode == expected_returncode)

    # check with python validation snippet if validate is specified
    validation_passing = False
    if returncode != -1:
        try:
            validation_passing = eval(validate, globals(), {**locals(), **kwargs})
        except Exception as e:
            print('   ', e)
            print(f'Failed to run validation func on: "{stdout}"  ->  {validate}')
            validation_passing = False

    passing = all((
        python_passing,
        duration_passing,
        returncode_passing,
        validation_passing,
    ))

    format_str = kwargs.get('format', '{stdout}')
    result = ''
    try:
        result = eval(f"f'{format_str}'")
    except Exception as e:
        print('   ', e)
        print(f'Failed to run format func on: "{stdout}"  -> {format_str}')


    run_output = {
        'cmd': CMD,
        'args': kwargs,

        'result': result,

        'passing': passing,
        'python_passing': python_passing,
        'duration_passing': duration_passing,
        'returncode_passing': returncode_passing,
        'validation_passing': validation_passing,

        'returncode': returncode,
        'stdout': stdout,
        'stderr': stderr,
        'exception': exception,

        'start_time': start_time,
        'end_time': end_time,
        'duration': duration.total_seconds(),
    }
    if not passing:
        print('   ', '\n    '.join(
            f'{key}: {val}'
            for key, val in run_output.items()
            if key != 'cmd'
        ))
    return run_output


import html
import os
import sys

from django.conf import settings
from django.core.asgi import get_asgi_application
from django.http import HttpResponse
from django.urls import path
from django.utils.crypto import get_random_string
from django.shortcuts import render

settings.configure(
    DEBUG=(os.environ.get('DEBUG', '').lower() in ('true', '1')),
    ALLOWED_HOSTS=[CONFIG.server.get('http_listen_host') or '*'],
    ROOT_URLCONF=__name__,
    SECRET_KEY=CONFIG.server.get('SECRET_KEY') or get_random_string(50),
    INSTALLED_APPS=[
        'django.contrib.humanize',
    ],
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [CONFIG.server.get('template_dir') or 'templates'],
        'APP_DIRS': False,
    }],
)


def get_runs(task_name: str):
    return [
        run_task(**CONFIG.tasks[task_name]),
        #run_task(**CONFIG.tasks[task_name]),
        #run_task(**CONFIG.tasks[task_name]),
    ]

def index(request):
    return render(request, 'index.html', {
        'hosts': CONFIG.hosts,
    })

def tasks(request):
    return render(request, 'tasks.html', {
        'tasks': {
            task_name: {
                **task,
                'runs': get_runs(task_name),
            }
            for task_name, task in CONFIG.tasks.items()
        },
    })


urlpatterns = [
    path('',        index),
    path('tasks',   tasks),
]


application = get_asgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    
    subcommand = sys.argv[1] if len(sys.argv) > 1 else 'server'

    print(f'[+] Starting Zervice.ZUP: {subcommand}...')
    try:
        if subcommand == 'server':
            execute_from_command_line([sys.argv[0], 'runserver', *sys.argv[1:]])
        elif subcommand == 'cron':
            cron(CONFIG)
        else:
            execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print('\n[X] Stopped.')
        raise SystemExit(0)
