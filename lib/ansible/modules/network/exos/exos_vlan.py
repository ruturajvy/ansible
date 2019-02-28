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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: exos_vlan
version_added: "2.8"
author: "Ruturaj Vyawahare (@ruturajvy)"
short_description: Manage VLANs on Extreme Networks EXOS network devices
description:
  - This module provides declarative management of VLANs
    on Extreme XOS network devices
notes:
  - Tested against EXOS 30.1.1.4
options:
  name:
    description:
      - Name of the VLAN.
  vlan_id:
    description:
      - ID of the VLAN. Range 1-4094.
    required: true
  interfaces:
    description:
      - List of interfaces that should be associated to the VLAN.
    required: true
  delay:
    description:
      - Delay the play should wait to check for declarative intent params values with default of 10 ms
    default: 10
  aggregate:
    description: List of VLANs definitions to be configured
  purge:
    description:
      - Purge VLANs not defined in the I(aggregate) parameter.
    type: bool
    default: no
  state:
    description:
      - State of the VLAN configuration.
    default: present
    choices: ['present', 'absent']
"""

EXAMPLES = """
- name: Create vlan
  exos_vlan:
    vlan_id: 100
    name: test-vlan
    state: present
- name: Add interfaces to VLAN
  exos_vlan:
    vlan_id: 100
    interfaces:
      - Ethernet 0/1
      - Ethernet 0/2
- name: Delete vlan
  exos_vlan:
    vlan_id: 100
    state: absent

- name: Create a VLAN configuration using aggregate
  exos_vlan:
    aggregate:
      - { vlan_id: 300, name: test_vlan_1 }
      - { vlan_id: 400, name: test_vlan_2 }
    state: present

"""

RETURN = """
commands:
  description: Configuration difference in terms of POST, PATCH and DELETE requests
  returned: when configuration is changed
  type: list
  sample:
    "requests": [
        {   "path": "/rest/restconf/data/openconfig-vlan:vlans/"
            "data": "{\"openconfig-vlan:vlan\": [{\"config\": {\"vlan-id\": 700, \"status\": \"ACTIVE\", \"name\": \"ansible700\", \"tpid\": \"oc-vlan-types:TPID_0x8100\"}}]}",
            "method": "POST"
        },
        {   "path": "/rest/restconf/data/openconfig-vlan:vlans/"
            "data": "{\"openconfig-vlan:vlan\": [{\"config\": {\"vlan-id\": 777, \"status\": \"ACTIVE\", \"name\": \"ansible777\", \"tpid\": \"oc-vlan-types:TPID_0x8100\"}}]}",
            "method": "POST"
        }
    ]
"""
import time
import json
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import conditional, remove_default_spec
from ansible.module_utils.network.exos.exos import send_requests

# Base path for the RESTconf API endpoint
def get_vlan_path():
  vlan_path = "/rest/restconf/data/openconfig-vlan:vlans/"
  return vlan_path

# Returns a JSON formatted body for POST and PATCH requests for vlan configuration
def make_vlan_body(vlan_id, name):
  vlan_body = {"openconfig-vlan:vlan":[{"config": {"vlan-id": None ,"status": "ACTIVE","tpid": "oc-vlan-types:TPID_0x8100","name": None}}]}
  vlan_config = vlan_body["openconfig-vlan:vlan"][0]['config']
  vlan_config['vlan-id'] = vlan_id
  vlan_config['name'] = name
  return json.dumps(vlan_body)

# Maps the current configuration to a list of dictionaries each with format {vlan_id: int, name: str, interfaces: list()}
def map_config_to_list(module):
    path = get_vlan_path()
    requests = [{"path":path}]
    resp = send_requests(module, requests = requests)
    old_config_list = list()
    for vlan_json in resp: 
      for vlan in vlan_json['openconfig-vlan:vlans']['vlan']:
          old_config_list.append({
          "name":vlan['config']['name'],
          "vlan_id": vlan['config']['vlan-id'],
          #interfaces to be implemented
          })
    return old_config_list

# Maps the required configuration to a list of dictionaries each with format {vlan_id: int, name: str, interfaces: list(), state: choices}
def map_params_to_list(module):
    params = module.params
    new_config_list = list()
    aggregate = params['aggregate']
    if aggregate:
      # Completes each dictionary with the common parameters in the element spec
        for item in aggregate:
            for key in item:
                if item.get(key) is None:
                    item[key] = module.params[key]
            d = item.copy()
            d['vlan_id'] = int(d['vlan_id'])
            validate_vlan_id(module, d['vlan_id'])
            new_config_list.append(d)
    else:
        validate_vlan_id(module, int(params['vlan_id']))
        new_config_list.append({
        "vlan_id":int(params['vlan_id']),
        "name":params['name'],
        "interfaces":params['interfaces'],
        "state":params['state']
        })
    return new_config_list

# Returns in the dictionary with the vlan in the list ( used for searching in old_config_list)    
def search_vlan_in_list(vlan_id, lst):
    for o in lst:
        if o['vlan_id'] == vlan_id:
            return o
    return None

def map_diff_to_requests(module, old_config_list, new_config_list):
    requests = list()
    purge = module.params['purge']
    for new_config in new_config_list:
        vlan_id = new_config['vlan_id']
        name = new_config['name']
        interfaces = new_config['interfaces']
        state = new_config['state']
        
        # Check if the VLAN is already configured
        old_vlan_dict = search_vlan_in_list(vlan_id, old_config_list)
        if state == 'absent':
            # Not working because of the DELETE method
            if old_vlan_dict:
                path = get_vlan_path() + "vlan=" + str(vlan_id)
                requests.append({"path": path, "method":"DELETE"})
        elif state == 'present':
            if not old_vlan_dict:
                if name:
                    path = get_vlan_path()
                    body = make_vlan_body(vlan_id, name)
                    requests.append({"path": path, "method":"POST", "data": body})
                if interfaces:
                    pass # To be implemented
            else:
                if name:
                    if name!=old_vlan_dict['name']:
                        path = get_vlan_path() + 'vlan=' + str(vlan_id)
                        body = make_vlan_body(vlan_id, name)                        
                        requests.append({"path": path , "method":"PATCH", "data": body})    
                if interfaces:
                    pass
    if purge:
      for old_config in old_config_list:
        new_vlan_dict = search_vlan_in_list(old_config['vlan_id'], new_config_list)
        if new_vlan_dict is None:
          path = get_vlan_path() + "vlan=" + str(old_config['vlan_id'])
          requests.append({"path": path, "method":"DELETE"})


    return requests

# Sends the HTTP requests to the switch API endpoints
def change_configuration(module,requests):
  send_requests(module, requests = requests)            

# Sanity check for the VLAN ID
def validate_vlan_id(module, vlan):
    if vlan and not 1 <= int(vlan) <= 4094:
        module.fail_json(msg='vlan_id must be between 1 and 4094')

# To check after a delay that the interfaces are in the VLAN 
def check_declarative_intent_params(new_config_list, module):
    if module.params['interfaces']:
        time.sleep(module.params['delay'])

        old_config_list = map_config_to_list(module)        # Contains all VLAN objects in new configuration 
        for newconfs in new_config_list:
            for i in newconfs['interfaces']:
                vlan_dict = search_vlan_in_list(newconfs['vlan_id'], old_config_list)
                if vlan_dict and 'interfaces' in vlan_dict and i not in vlan_dict['interfaces']:
                    module.fail_json(msg="Interface %s not configured on vlan %s" % (i, newconfs['vlan_id']))
def main():
    """ main entry point for module execution
    """
    element_spec = dict(
        vlan_id=dict(type='int'),
        name=dict(),
        interfaces=dict(type='list'),
        delay=dict(default=10, type='int'),
        state=dict(default='present',
                   choices=['present', 'absent'])
    )

    aggregate_spec = deepcopy(element_spec)
    aggregate_spec['vlan_id'] = dict(required=True)

    # Removes default values from aggregate spec
    remove_default_spec(aggregate_spec)

    argument_spec = dict(
        aggregate=dict(type='list', elements='dict', options=aggregate_spec),
        purge=dict(default=False, type='bool')
    )

    argument_spec.update(element_spec)

    required_one_of = [['vlan_id', 'aggregate']]
    mutually_exclusive = [['vlan_id', 'aggregate']]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_one_of=required_one_of,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)
    
    warnings = list()
    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings
    old_config_list = map_config_to_list(module)
    new_config_list = map_params_to_list(module)
    
    requests = map_diff_to_requests(module, old_config_list, new_config_list)
    result['requests'] = requests

    if requests:
        if not module.check_mode:
            change_configuration(module, requests)
        result['changed'] = True

    if result['changed']:
        check_declarative_intent_params(new_config_list, module)
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()
  