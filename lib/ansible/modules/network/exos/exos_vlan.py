#!/usr/bin/python
#
# (c) 2018 Extreme Networks Inc.
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
version_added: "2.7"
author: "Ruturaj Vyawahare (@ruturajvy)"
short_description: Manage VLANs on Extreme Networks EXOS network devices
description:
  - This module provides declarative management of VLANs
    on Extreme XOS network devices
notes:
  - Tested against EXOS 30.2.0.12
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
      - { vlan_id: 300, name: test_vlan_1, description: test_vlan 1 }
      - { vlan_id: 400, name: test_vlan_2, description: test_vlan 2 } 
"""

RETURN = """
commands:
  description: Configuration difference before and after applying change.
  returned: when configuration is changed
  type: list
  sample:
    - vlan 100
    - name test-vlan
"""
import json
from ansible.module_utils.urls import open_url
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import conditional, remove_default_spec
from ansible.module_utils.network.exos.exos import HttpApi as web

 
def map_params_to_obj(self,module,params=None):
    if not params:
        params = module.params
    aggregate = params['aggreagate']
    if aggregate:
        for item in aggregate:
        for key in item:
            if item.get(key) is None:
            pass
# Maps the current configuration to a list of dictionaries with each dictionary having name, vlan_id, interfaces as keys
def map_config_to_obj(self,module):
    resp = web.send_requests()
    vlan_json = json.loads(resp)
    config_list = list()
    for vlan in vlan_json['openconfig-vlan:vlans']['vlan']:
        config_list.append({
        'name':vlan['config']['name'],
        'vlan_id': vlan['config']['vlan_id'],
        'interfaces': [item['interface-ref']['state'] for item in vlan['members']['member']]
        })
    return config_list
def map_diff_to_requests(self,module, diff):
    old_config, new_config = diff


def validate_vlan_id(value, module):
    if value and not 1 <= value <= 4094:
        module.fail_json(msg='vlan_id must be between 1 and 4094')

def to_param_list(module):
    aggregate = module.params.get('aggregate')
    if aggregate:
        if isinstance(aggregate, dict):
            return [aggregate]
        else:
            return aggregate
    else:
        return [module.params]
# Map config to object  
# def list_vlans():   
#     vlan_json = json.loads(open_url(list_url, method='GET', url_username='admin', url_password='').read())
#     print(json.dumps(vlan_json))
#     name_list = [vlistitem['config']['name'] for vlistitem in vlan_json['openconfig-vlan:vlans']['vlan']]
#     vlan_id_list = [vlist['config']['vlan-id'] for vlist in vlan_json['openconfig-vlan:vlans']['vlan']]
#     vlan_tuple_list = zip(name_list, vlan_id_list)
#     print(vlan_tuple_list)
#     return vlan_tuple_list
# # Check with the current config
# def validate_vlan(vlan_id, name):
#     tuple_vlans = list_vlans()
#     for item in tuple_vlans:
#         if item[0]==name:
#             return 1
#         if item[1]==vlan_id:
#             return 2
#     return 0

        
# def create_vlan(vlan_id, name):
#     if validate_vlan(vlan_id,name)==1:
#         error_msg = "Cannot create vlan. Vlan with the name " + name + " already exists"
#         print(error_msg)
#         return
#         #.fail_json(msg = error_msg)
#     elif validate_vlan(vlan_id,name)==2:
#         error_msg = "Cannot create vlan. Vlan with the id " + str(vlan_id) + " already exists"
#         print(error_msg)
#         return
#         #.fail_json(msg = error_msg)
#     data = build_vlan_json(vlan_id, name)
#     resp = open_url(post_vlan, method='POST', data = data, headers = { "Content-Type": "application/json", "Accept": "application/json" }, url_username='admin', url_password='')
#     print(resp.read())

# def build_vlan_json(vlan_id, name):
#     vlan_json_serialized = json.dumps({"openconfig-vlan:vlan":[{"config": {"vlan-id": str(vlan_id) ,"status": "ACTIVE","tpid": "oc-vlan-types:TPID_0x8100","name": name}}]})
#     #vlan_json_deserialized = json.loads(vlan_json_serialized)
#     print(vlan_json_serialized)
#     return vlan_json_serialized

# def update_vlan_name(vlan_id,name):
#     data = json.dumps({"openconfig-vlan:vlan":[{"config": {"vlan-id": str(vlan_id) ,"status": "ACTIVE","tpid": "oc-vlan-types:TPID_0x8100","name": name}}]})
#     try:
#         rsp = open_url(post_vlan +'vlan='+str(vlan_id), method='PATCH', data = data, headers = { "Content-Type": "application/json", "Accept": "application/json" }, url_username='admin', url_password='')
#         print(rsp.read())
#     # except HTTPError as e:
#     #    print("The VLAN already exists: HTTPError: %s" % e.code)
#     except:
#         print("Failed to update VLAN")

# def delete_vlan_by_id(vlan_id):
#     try:
#         rsp = open_url(post_vlan + 'vlan=' + str(vlan_id), method='DELETE', headers = { "Content-Type": "application/json", "Accept": "application/json" }, url_username='admin', url_password='')
#         print(rsp.read())
#     except HTTPError as e:
#         print("HTTP Error %s" %e.code)
    
# def delete_vlan_by_name(name):
#     tuple_vlans = list_vlans()
#     for item in tuple_vlans:
#         if item[0] == name:
#             rsp = open_url(post_vlan + 'vlan=' + str(item[1]), method='DELETE', headers = { "Content-Type": "application/json", "Accept": "application/json" }, url_username='admin', url_password='')
#             print(rsp.read())
#             return
#     print("The VLAN does not exist")
#     return


def main():
    """ main entry point for module execution
    """
    element_spec = dict(
        vlan_id=dict(type='int'),
        name=dict(type='str'),
        interfaces=dict(type='list'),
        delay=dict(default=10, type='int'),
        state=dict(default='present',
                   choices=['present', 'absent'])
    )
    aggregate_spec = deepcopy(element_spec)
    aggregate_spec['vlan_id'] = dict(required=True)
    argument_spec = dict(
        aggregate=dict(type='list', elements='dict'
        , options=aggregate_spec),
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

    want = map_params_to_obj(module)
    have = map_config_to_obj(module)
    requests = map_diff_to_requests((want, have), module)
    

    if commands:
        if not module.check_mode:
            load_config(module, commands)
        result['changed'] = True

    if result['changed']:
        check_declarative_intent_params(want, module)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
