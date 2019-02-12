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

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.network.common.utils import to_list
from ansible.plugins.httpapi import HttpApiBase
import ansible.module_utils.six.moves.http_cookiejar as cookiejar


OPTIONS = {
    'format': ['json'],
    'diff_match': ['line', 'strict', 'exact', 'none'],
    'diff_replace': ['line', 'block', 'config'],
    'output': ['json']
}


class HttpApi(HttpApiBase):

    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self._device_info = None
        self._auth_token = cookiejar.CookieJar()

    def login(self, username, password):
        auth_path = '/auth/token'
        credentials = { 'username': username, 'password': password }
        self.send_request(data=None, path=auth_path, method='GET', headers=credentials)

    def logout(self):
        pass

    def handle_httperror(self, exc):
        return False

    def send_request(self, data, **message_kwargs):
        response, response_data = self.connection.send(message_kwargs.pop('path'), data, cookies=self._auth_token, **message_kwargs)
        try:
            response_data = json.loads(to_text(response_data.getvalue()))
        except ValueError:
            raise ConnectionError('Response was not valid JSON, got {0}'.format(
                to_text(response_data.getvalue())
            ))
        return response_data
