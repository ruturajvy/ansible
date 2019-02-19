# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2016 Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import json
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback, return_values
from ansible.module_utils.network.common.utils import to_list, ComplexList
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.connection import Connection, ConnectionError

_DEVICE_CONNECTION = None

class Cli:
    def __init__(self, module):
        self._module = module
        self._device_configs = {}
        self._connection = None

    def get_capabilities(self):
        """Returns platform info of the remove device
        """
        connection = self._get_connection()
        return json.loads(connection.get_capabilities())

    def _get_connection(self):
        if not self._connection:
            self._connection = Connection(self._module._socket_path)
        return self._connection

    def get_config(self, flags=None):
        """Retrieves the current config from the device or cache
        """
        flags = [] if flags is None else flags
        try:
            return self._device_configs
        except KeyError:
            connection = self._get_connection()
            try:
                out = connection.get_config(flags=flags)
            except ConnectionError as exc:
                self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
            cfg = to_text(out, errors='surrogate_then_replace').strip()
            self._device_configs = cfg
            return cfg

    def load_config(self, commands):
        """Loads the configuration onto the remote devices
        """
        connection = self._get_connection()
        out = connection.edit_config(commands)

    def run_commands(self, commands, check_rc=True):
        """Runs list of commands on remote device and returns results
        """
        connection = self._get_connection()
        try:
            response = connection.run_commands(commands=commands, check_rc=check_rc)
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
        return response

    def send_requests(self, requests):
        # TO DO : Error - Not Supported
        pass


class HttpApi:
    def __init__(self, module):
        self._module = module
        self._device_configs = {}
        self._connection_obj = None

    def get_capabilities(self):
        """Returns platform info of the remove device
        """
        try:
            capabilities = self._connection.get_capabilities()
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

        return json.loads(capabilities)

    @property
    def _connection(self):
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)
        return self._connection_obj

    def get_config(self, commands):
        """Retrieves the current config from the device or cache
        """
        # TO DO
        pass

    def load_config(self, commands):
        """Loads the configuration onto the remote devices
        """
        # TO DO - Not supported? Or Just run_commands?
        pass

    def run_commands(self, commands, check_rc=True):
        """Runs list of commands on remote device and returns results
        """
        try:
            response = self._connection.run_commands(commands=commands, check_rc=check_rc)
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
        return response

    def send_requests(self, requests):
        """Send a list of http requests to remote device and return results
        """
        if requests is None:
            raise ValueError("'requests' value is required")

        responses = list()
        for req in to_list(requests):
            if isinstance(req, Mapping):
                path = req.pop('path')
            try:
                response = self._connection.send_request(path=path, **req)
            except ConnectionError as exc:
                self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
            responses.append(response)
        return responses


def get_capabilities(module):
    conn = get_connection(module)
    return conn.get_capabilities()

def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        connection_proxy = Connection(module._socket_path)
        cap = json.loads(connection_proxy.get_capabilities())
        if cap['network_api'] == 'cliconf':
            conn = Cli(module)
        elif cap['network_api'] == 'exosapi':
            conn = HttpApi(module)
        else:
            module.fail_json(msg='Invalid connection type %s' % cap['network_api'])
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION

def get_config(module, flags=None):
    flags = None if flags is None else flags
    conn = get_connection(module)
    return conn.get_config(flags)

def load_config(module, config):
    conn = get_connection(module)
    return conn.load_config(config)

def run_commands(module, commands, check_rc=True):
    conn = get_connection(module)
    return conn.run_commands(to_command(module, commands), check_rc=check_rc)

def to_command(module, commands):
    transform = ComplexList(dict(
        command=dict(key=True),
        output=dict(default='text'),
        prompt=dict(type='list'),
        answer=dict(type='list'),
        sendonly=dict(type='bool', default=False),
        check_all=dict(type='bool', default=False),
    ), module)
    return transform(to_list(commands))

def send_requests(module, requests):
    conn = get_connection(module)
    return conn.send_requests(to_request(module, requests))

def to_request(module, requests):
    transform = ComplexList(dict(
        request=dict(key=True),
        method=dict(),
        data=dict(),
    ), module)
    return transform(to_list(requests))
