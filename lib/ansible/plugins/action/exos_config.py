#
# Copyright 2015 Peter Sprygada <psprygada@ansible.com>
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

from ansible import constants as C
from ansible.plugins.action.network import ActionModule as ActionNetworkModule


class ActionModule(ActionNetworkModule):

    def run(self, tmp=None, task_vars=None):
        del tmp  # tmp no longer has any effect

        self._config_module = True
        return super(ActionModule, self).run(task_vars=task_vars)


    @staticmethod
    def exosapi_implementation(provider, play_context):
        provider['transport'] = 'exosapi'

        if provider.get('host') is None:
            provider['host'] = play_context.remote_addr

        if provider.get('port') is None:
            default_port = 443 if provider['use_ssl'] else 80
            provider['port'] = int(play_context.port or default_port)

        if provider.get('timeout') is None:
            provider['timeout'] = C.PERSISTENT_COMMAND_TIMEOUT

        if provider.get('username') is None:
            provider['username'] = play_context.connection_user

        if provider.get('password') is None:
            provider['password'] = play_context.password

        if provider.get('use_ssl') is None:
            provider['use_ssl'] = False

        return provider