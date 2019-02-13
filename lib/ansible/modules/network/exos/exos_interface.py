#!/usr/bin/python
#
# (c) 2019 Extreme Networks Inc.
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

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = """
---
module: exos_interface
version_added: "2.6"
author:
  - "Olen Stokes (@ostokes)"
  - "Ujwal Komarla (@ujwalkomarla)"
short_description: Manage Interfaces on Extreme EXOS network devices
description:
  - This module provides declarative management of Interfaces
    on Extreme EXOS network devices.
notes:
  - Tested against EXOS 22.6.1.4
options:
  name:
    description:
      - Full name of the interface, i.e. Port 1, Port 1:4, Port 3:4.
    required: true
    aliases: ['interface']
  description:
    description:
      - Description of Interface.
  enabled:
    description:
      - Interface link status.
    default: True
    type: bool
  speed:
    description:
      - Interface link speed.
  mtu:
    description:
      - Maximum size of transmit packet. Must be a number between 1500 and 9216.
  tx_rate:
    description:
      - Transmit rate in bits per second (bps).
      - This is state check parameter only.
  rx_rate:
    description:
      - Receiver rate in bits per second (bps).
      - This is state check parameter only.
  neighbors:
    description:
      - Check the operational state of given interface C(name) for LLDP neighbor.
      - This is state check parameter only.
      - The following suboptions are available.
    suboptions:
        host:
          description:
            - "LLDP neighbor host for given interface C(name)."
        port:
          description:
            - "LLDP neighbor port to which given interface C(name) is connected."
  aggregate:
    description: List of Interfaces definitions.
  delay:
    description:
      - Time in seconds to wait before checking for the operational state on remote
        device. This wait is applicable for operational state argument which are
        I(state) with values C(up)/C(down), I(tx_rate) and I(rx_rate).
    default: 10
  state:
    description:
      - State of the Interface configuration, C(up) means present and
        operationally up and C(down) means present and operationally C(down)
    default: present
    choices: ['present', 'absent', 'up', 'down']
  duplex:
    description:
      - Interface link status.
      default: full
      choices: ['full', 'half', 'auto']
"""

EXAMPLES = """
- name: configure interface
  exos_interface:
      name: Port 2
      description: test-interface
      speed: 1000
      mtu: 9216

- name: make interface up
  exos_interface:
    name: Port 2
    enabled: True

- name: make interface down
  exos_interface:
    name: Port 3
    enabled: False

- name: Check intent arguments
  exos_interface:
    name: Port 2
    state: up
    tx_rate: 1000
    rx_rate: 1000

- name: Check neighbors intent arguments
  exos_interface:
    name: Port 1
    neighbors:
    - port: Port 1
      host: EXOS

- name: Config + intent
  exos_interface:
    name: Port 4
    enabled: False
    state: down

- name: Add interface using aggregate
  exos_interface:
    aggregate:
    - { name: Port 1, mtu: 1548, description: test-interface-1 }
    - { name: Port 2, mtu: 1548, description: test-interface-2 }
    speed: 10000
    state: present

"""

RETURN = """
"""

import json
from copy import deepcopy
from time import sleep
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.exos.exos import EXOS_API_INSTANCE
from ansible.module_utils.network.common.utils import conditional, remove_default_spec



class EXOS_INTERFACE(EXOS_API_INSTANCE):

    #COMMANDS = list()

    def map_params_to_obj(self):
        pass

    def map_config_to_obj(self):
        pass

    def map_diff_to_requests(self):
        pass
        return False

    def load_config(self):
        pass

    def check_declarative_intent_params(self):
        pass
        return False


    #    self.module = module
    #    self.facts = dict()
    #    self.responses = None

    #def populate(self):
    #    self.responses = run_commands(self.module, self.COMMANDS)

    #def run(self, cmd):
    #    return run_commands(self.module, cmd)


def main():
    """ main entry point for module execution
    """
    neighbors_spec = dict(
        host=dict(),
        port=dict()
    )

    element_spec = dict(
        name=dict(aliases=['interface']),
        description=dict(),
        speed=dict(),
        mtu=dict(),
        enabled=dict(default=True, type='bool'),
        tx_rate=dict(),
        rx_rate=dict(),
        neighbors=dict(type='list', elements='dict', options=neighbors_spec),
        delay=dict(default=10, type='int'),
        state=dict(default='up',
                   choices=['present', 'absent', 'up', 'down']),
        duplex=dict(choices=['full', 'half', 'auto'])
    )

    aggregate_spec = deepcopy(element_spec)
    aggregate_spec['name'] = dict(aliases=['interface'], required=True)

    # remove default in aggregate spec, to handle common arguments
    remove_default_spec(aggregate_spec)

    argument_spec = dict(
        aggregate=dict(type='list', elements='dict', options=aggregate_spec),
    )

    argument_spec.update(element_spec)

    required_one_of = [['name', 'aggregate']]
    mutually_exclusive = [['name', 'aggregate']]
    required_if = [('duplex', 'full', ['speed']), ('duplex', 'half', ['speed'])]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_one_of=required_one_of,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True,
                           required_if=required_if)
    warnings = list()

    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings

    exos_interface = EXOS_INTERFACE(module)

    # Map playbook requested parameters into object
#    want = map_params_to_obj(module)
    exos_interface.map_params_to_obj()

    # Map existing configuration into object
#    have = map_config_to_obj(module)
    exos_interface.map_config_to_obj()

    # Map the differences between the requested parameters and the existing parameters into EXOS API Requests
#    requests = map_diff_to_requests((want, have), module)
    requests = exos_interface.map_diff_to_requests()
    # FIX ME! result['commands'] = commands

    # Send the commands to the EXOS device
    if requests:
        if not module.check_mode:
            # FIX ME! load_config(module, commands)
            exos_interface.load_config()
            result['changed'] = True

    if result['changed']:
        # Check that the commands resulted in the expected configuration
#        failed_conditions = check_declarative_intent_params(module, want)
        failed_conditions = exos_interface.check_declarative_intent_params()
        if failed_conditions:
            msg = 'One or more conditional statements have not been satisfied'
            module.fail_json(msg=msg, failed_conditions=failed_conditions)

    module.exit_json(**result)


if __name__ == '__main__':
    main()