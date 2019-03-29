#!/usr/bin/env python3

# OpenBACH is a generic testbed able to control/configure multiple
# network/physical entities (under test) and collect data from them. It is
# composed of an Auditorium (HMIs), a Controller, a Collector and multiple
# Agents (one for each network entity that wants to be tested).
#
#
# Copyright © 2016 CNES
#
#
# This file is part of the OpenBACH testbed.
#
#
# OpenBACH is a free software : you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.


"""Frontend scripts base tools

Define a structure able to specify a parser and an
action to send to the OpenBACH backend.

This module provides the boilerplate around managing
users authentication and pretty-printing the response
from the backend.
"""


__author__ = 'Viveris Technologies'
__credits__ = '''Contributors:
 * Adrien THIBAUD <adrien.thibaud@toulouse.viveris.com>
 * Mathias ETTINGER <mathias.ettinger@toulouse.viveris.com>
'''

import json
import fcntl
import socket
import struct
import pprint
import getpass
import datetime
import argparse
import warnings
from time import sleep
from pathlib import Path
from contextlib import suppress

import requests


def get_interfaces():
    """Return the name of the first network interface found"""
    yield from (
            iface.name
            for iface in Path('/sys/class/net/').iterdir()
            if iface.name != 'lo')
    yield 'lo'


def get_ip_address(ifname):
    """Return the IP address associated to the given interface"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode())
    )[20:24])


def get_default_ip_address():
    """Return the first public IP address found"""
    for iface in get_interfaces():
        with suppress(OSError):
            return get_ip_address(iface)


def read_controller_configuration(filename='controller'):
    default_ip = get_default_ip_address()
    try:
        stream = open(filename)
    except OSError:
        message = (
                'File not found: \'{}\'. Using one of your '
                'IP address instead as the default: \'{}\'.'
                .format(filename, default_ip))
        warnings.warn(message, RuntimeWarning)
        return default_ip, None, None

    with stream:
        try:
            content = json.load(stream)
        except json.JSONDecodeError:
            stream.seek(0)
            controller = stream.readline().strip()
            password = None
            login = None
        else:
            if isinstance(content, str):
                content = {'controller': content}
            if not isinstance(content, dict):
                message = (
                        'Content of the \'controller\' file '
                        'is not a JSON string or dictionnary: '
                        'will consider it as an empty file.')
                warnings.warn(message, RuntimeWarning)
                content = {}
            controller = content.get('controller')
            password = content.get('password')
            login = content.get('login')

    if not controller:
        message = (
                'Empty file: \'{}\'. Using one of your '
                'IP address instead as the default: \'{}\'.'
                .format(filename, default_ip))
        warnings.warn(message, RuntimeWarning)
        controller = default_ip

    return controller, login, password


def pretty_print(response):
    """Helper function to nicely format the response
    from the server.
    """

    if response.status_code != 204:
        try:
            content = response.json()
        except ValueError:
            content = response.text
        pprint.pprint(content, width=120)

    response.raise_for_status()


class FrontendBase:
    WAITING_TIME_BETWEEN_STATES_POLL = 5  # seconds

    @classmethod
    def autorun(cls):
        self = cls()
        try:
            self.parse()
            self.execute()
        except requests.RequestException as error:
            self.parser.error(str(error))
        except ActionFailedError as error:
            self.parser.error(error.message)

    def __init__(self, description):
        controller, login, password = read_controller_configuration()
        self.parser = argparse.ArgumentParser(
                description=description,
                epilog='Backend-specific arguments can be specified by '
                'providing a file called \'controller\' in the same folder '
                'than this script. This file can contain a JSON dictionary '
                'whose values will act as defaults for the arguments or '
                'some text whose first line will be interpreted as the '
                '\'controller\' argument default value. If no password is '
                'specified using either this file or the command-line, it '
                'will be prompted without echo.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        backend = self.parser.add_argument_group('backend')
        backend.add_argument(
                '--controller', default=controller,
                help='address at which the contoller is listening')
        backend.add_argument(
                '--login', '--username', default=login,
                help='username used to authenticate as')
        backend.add_argument(
                '--password', help='password used to authenticate as')
        self._default_password = password

        self.session = requests.Session()

    def parse(self, args=None):
        self.args = args = self.parser.parse_args(args)
        if args.controller is None:
            self.parser.error(
                    'error: no controller was specified '
                    'and the default cannot be found')
        self.base_url = url = 'http://{}:8000/'.format(args.controller)
        login = args.login
        if login:
            password = args.password or self._default_password
            if password is None:
                password = getpass.getpass('OpenBACH password: ')
            credentials = {'login': login, 'password': password}
            response = self.session.post(url + 'login/', json=credentials)
            response.raise_for_status()

        return args

    def date_to_timestamp(self, fmt='%Y-%m-%d %H:%M:%S.%f'):
        date = getattr(self.args, 'date', None)
        if date is not None:
            try:
                date = datetime.datetime.strptime(date, fmt)
            except ValueError:
                self.parser.error(
                        'date and time does not respect '
                        'the {} format'.format(fmt))
            else:
                return int(date.timestamp() * 1000)

    def execute(self, show_response_content=True):
        pass

    def request(self, verb, route, show_response_content=True, files=None, **kwargs):
        verb = verb.upper()
        url = self.base_url + route
        if verb == 'GET':
            response = self.session.get(url, params=kwargs)
        else:
            if files is None:
                response = self.session.request(verb, url, json=kwargs)
            else:
                response = self.session.request(verb, url, data=kwargs, files=files)
        if show_response_content:
            pretty_print(response)
        return response

    def wait_for_success(self, status=None, valid_statuses=(200, 204), show_response_content=True):
        while True:
            sleep(self.WAITING_TIME_BETWEEN_STATES_POLL)
            response = self.query_state()
            response.raise_for_status()
            try:
                content = response.json()
            except ValueError:
                raise ActionFailedError(
                        'Server returned non-JSON response: {}'.format(response.text),
                        response.status_code)

            if status:
                content = content[status]
            returncode = content['returncode']
            if returncode != 202:
                if show_response_content:
                    pprint.pprint(content['response'], width=200)
                if returncode not in valid_statuses:
                    raise ActionFailedError(**content)
                return

    def query_state(self):
        return self.session.get(self.base_url)


class ActionFailedError(Exception):
    def __init__(self, response, returncode, **kwargs):
        super().__init__(response)
        self.message = response