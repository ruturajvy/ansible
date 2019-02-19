# Copyright (c) 2019 Extreme Networks.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
author:
  - "Ujwal Komarla (@ujwalkomarla)"
httpapi: exos
short_description: Use EXOS REST APIs to communicate with EXOS platform
description:
  - This exos plugin provides low level abstraction api's for
    sending REST API requests to exos network devices and receiving JSON responses.
version_added: "2.8"
"""

import json
import re
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.network.common.utils import to_list
from ansible.plugins.httpapi import HttpApiBase
import ansible.module_utils.six.moves.http_cookiejar as cookiejar
from ansible.module_utils.common._collections_compat import Mapping

class HttpApi(HttpApiBase):

    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self._device_info = None
        self._auth_token = cookiejar.CookieJar()

    def login(self, username, password):
        auth_path = '/auth/token'
        credentials = {'username': username, 'password': password }
        self.send_request(path=auth_path, data=json.dumps(credentials), method='POST')

    def logout(self):
        pass

    def handle_httperror(self, exc):
        return False

    def send_request(self, path, data=None, method='GET', **message_kwargs):
        headers = {'Content-Type': 'application/json'}
        response, response_data = self.connection.send(path, data, cookies=self._auth_token, headers=headers, **message_kwargs)
        try:
            response_data = json.loads(to_text(response_data.getvalue()))
        except ValueError:
            raise ConnectionError('Response was not valid JSON, got {0}'.format(
                to_text(response_data.getvalue())
            ))
        return response_data

    def run_commands(self, commands, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        headers = {'Content-Type': 'application/json'}
        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            cmd['command'] = strip_run_script_cli2json(cmd['command'])

            output = cmd.pop('output', None)
            if output and output not in self.get_option_values().get('output'):
                raise ValueError("'output' value is %s is invalid. Valid values are %s" % (output, ','.join(self.get_option_values().get('output'))))

            #TO DO: FIELDS NOT SUPPORTED
            if ('prompt', 'answer') in cmd:
                pass
            data = request_builder(cmd['command'])

            response, response_data = self.connection.send('/jsonrpc', data, cookies=self._auth_token, headers=headers, method='POST')
            try:
                response_data = json.loads(to_text(response_data.getvalue()))
            except ValueError:
                raise ConnectionError('Response was not valid JSON, got {0}'.format(
                    to_text(response_data.getvalue())
                ))

            if output and output == 'text':
                cliOutput = getCLIoutput(response_data)
                if not cliOutput:
                    raise ValueError("Response doesn't have the CLIoutput field, got {0}".format(response_data))
                response_data = cliOutput
            #handle_error(response_data)    # Invoker should check for 'status' of the object before using it.
            responses.append(response_data)
        return responses

    def get_device_info(self):
        device_info = {}
        device_info['network_os'] = 'exos'

        reply = self.run_commands({'command': 'show switch detail', 'output':'text'})
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'ExtremeXOS version  (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'System Type: +(\S+)', data)
        if match:
            device_info['network_os_model'] = match.group(1)

        match = re.search(r'SysName: +(\S+)', data)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    def get_device_operations(self):
        return {
                    'supports_diff_replace': False,        # identify if config should be merged or replaced is supported
                    'supports_commit': False,              # identify if commit is supported by device or not
                    'supports_rollback': False,            # identify if rollback is supported or not
                    'supports_defaults': True,             # identify if fetching running config with default is supported
                    'supports_commit_comment': False,      # identify if adding comment to commit is supported of not
                    'supports_onbox_diff': True,           # identify if on box diff capability is supported or not
                    'supports_generate_diff': True,       # identify if diff capability is supported within plugin
                    'supports_multiline_delimiter': False, # identify if multiline demiliter is supported within config
                    'supports_diff_match': True,           # identify if match is supported
                    'supports_diff_ignore_lines': True,    # identify if ignore line in diff is supported
                    'supports_config_replace': False,      # identify if running config replace with candidate config is supported
                    'supports_admin': False,               # identify if admin configure mode is supported or not
                    'supports_commit_label': False         # identify if commit label is supported or not
        }

    def get_option_values(self):
        return {
            'format': ['text', 'json'],
            'diff_match': ['line', 'strict', 'exact', 'none'],
            'diff_replace': ['line', 'block'],
            'output': ['text', 'json']
        }

    def get_capabilities(self):
        result = {}
        result['rpc'] = []
        result['device_info'] = self.get_device_info()
        result['device_operations'] = self.get_device_operations()
        result.update(self.get_option_values())
        result['network_api'] = 'exosapi'
        return json.dumps(result)

def request_builder(command, reqid=""):
    return json.dumps(dict(jsonrpc='2.0', id=reqid, method='cli', params=to_list(command)))

def strip_run_script_cli2json(command):
    if to_text(command, errors="surrogate_then_replace").startswith('run script cli2json.py'):
        command = str(command).replace('run script cli2json.py', '')
    return command

def getKeyInResult(response, key):
    keyOut = None
    for item in response:
        if key in item:
            keyOut = item[key]
            break
    return keyOut
