#
# (c) 2017 Red Hat Inc.
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
cliconf: exos
short_description: Use exos cliconf to run command on Extreme EXOS platform
description:
  - This exos plugin provides low level abstraction apis for
    sending and receiving CLI commands from Extreme EXOS network devices.
version_added: "2.6"
"""

import re
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.common._collections_compat import Mapping
from ansible.plugins.cliconf import CliconfBase


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}
        device_info['network_os'] = 'exos'

        reply = self.get('show switch detail')
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

    def get_config(self, source='running', format='text', flags=None):
        options_values = self.get_option_values()
        if format not in options_values['format']:
            raise ValueError("'format' value %s is invalid. Valid values are %s" % (format, ','.join(options_values['format'])))

        lookup = {'running': 'show configuration', 'startup': 'debug cfgmgr show configuration file'}
        if source not in lookup:
            raise ValueError("fetching configuration from %s is not supported" % source)

        if source == 'running':
            cmd = lookup[source]
        else:
            cmd = lookup[source]
            reply = self.get('show switch | include "Config Selected"')
            # DEFAULTS - No configuration to show # TO DO
            data = to_text(reply, errors='surrogate_or_strict').strip()
            match = re.search(r': +(\S+)\.cfg', data)
            if match:
                cmd += ' '.join( match.group(1))
                cmd = cmd.strip()

        cmd += ' '.join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)

    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):
        operations = self.get_device_operations()
        self.check_edit_config_capability(operations, candidate, commit, replace, comment)

    def get(self, command, prompt=None, answer=None, sendonly=False, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, check_all=check_all)

    def get_diff(self, candidate=None, running=None, diff_match='strict', diff_ignore_lines=None, path=None, diff_replace='line'):
        pass
        # TO DO - On device diff available

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            output = cmd.pop('output', None)
            if output:
                cmd['command'] = self._get_command_with_output(cmd['command'], output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc is True:
                    raise
                out = getattr(e, 'err', e)

            if out is not None:
                try:
                    out = to_text(out, errors='surrogate_or_strict').strip()
                except UnicodeError:
                    raise ConnectionError(message=u'Failed to decode output from %s: %s' % (cmd, to_text(out)))

                if output and output == 'json':
                    try:
                        out = json.loads(out)
                    except ValueError:
                        raise ConnectionError('Response was not valid JSON, got {0}'.format(
                            to_text(out)
                        ))
                responses.append(out)

        return responses

    def get_device_operations(self):
        return {
                    'supports_diff_replace': False,        # identify if config should be merged or replaced is supported
                    'supports_commit': False,              # identify if commit is supported by device or not
                    'supports_rollback': False,            # identify if rollback is supported or not
                    'supports_defaults': True,             # identify if fetching running config with default is supported
                    'supports_commit_comment': False,      # identify if adding comment to commit is supported of not
                    'supports_onbox_diff': True,           # identify if on box diff capability is supported or not
                    'supports_generate_diff': True,        # identify if diff capability is supported within plugin
                    'supports_multiline_delimiter': False, # identify if multiline delimiter is supported within config
                    'supports_diff_match': True,           # identify if match is supported
                    'supports_diff_ignore_lines': True,    # identify if ignore line in diff is supported
                    'supports_config_replace': False,      # identify if running config replace with candidate config is supported
                    'supports_admin': False,               # identify if admin configure mode is supported or not
                    'supports_commit_label': False,        # identify if commit label is supported or not
                    'supports_replace': False
        }

    def get_option_values(self):
        return {
            'format': ['text', 'json'],
            'diff_match': ['strict'],
            'diff_replace': ['line', 'block'],
            'output': ['text', 'json']
        }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result['rpc'] += ['run_commmands']
        result['device_operations'] = self.get_device_operations()
        result['device_info'] = self.get_device_info()
        result.update(self.get_option_values())
        return json.dumps(result)

    def _get_command_with_output(self, command, output):
        if output not in self.get_option_values().get('output'):
            raise ValueError("'output' value is %s is invalid. Valid values are %s" % (output, ','.join(self.get_option_values().get('output'))))

        if output == 'json' and not command.startswith('run script cli2json.py'):
            cmd = 'run script cli2json.py %s' % command
        else:
            cmd = command
        return cmd
