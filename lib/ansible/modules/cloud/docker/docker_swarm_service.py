#!/usr/bin/python
#
# (c) 2017, Dario Zanzico (git@dariozanzico.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}
DOCUMENTATION = '''
---
module: docker_swarm_service
author: "Dario Zanzico (@dariko), Jason Witkowski (@jwitko)"
short_description: docker swarm service
description:
  - Manages docker services via a swarm manager node.
version_added: "2.7"
options:
  name:
    description:
      - Service name.
      - Corresponds to the C(--name) option of C(docker service create).
    type: str
    required: yes
  image:
    description:
      - Service image path and tag.
      - Corresponds to the C(IMAGE) parameter of C(docker service create).
    type: str
    required: yes
  resolve_image:
    description:
      - If the current image digest should be resolved from registry and updated if changed.
    type: bool
    default: yes
    version_added: 2.8
  state:
    description:
      - Service state.
    type: str
    required: yes
    default: present
    choices:
      - present
      - absent
  args:
    description:
      - List arguments to be passed to the container.
      - Corresponds to the C(ARG) parameter of C(docker service create).
    type: list
  command:
    description:
      - Command to execute when the container starts.
      - A command may be either a string or a list or a list of strings.
      - Corresponds to the C(COMMAND) parameter of C(docker service create).
    type: raw
    version_added: 2.8
  constraints:
    description:
      - List of the service constraints.
      - Corresponds to the C(--constraint) option of C(docker service create).
    type: list
  placement_preferences:
    description:
      - List of the placement preferences as key value pairs.
      - Corresponds to the C(--placement-pref) option of C(docker service create).
      - Requires API version >= 1.27.
    type: list
    version_added: 2.8
  healthcheck:
    description:
      - Configure a check that is run to determine whether or not containers for this service are "healthy".
        See the docs for the L(HEALTHCHECK Dockerfile instruction,https://docs.docker.com/engine/reference/builder/#healthcheck)
        for details on how healthchecks work.
      - "I(interval), I(timeout) and I(start_period) are specified as durations. They accept duration as a string in a format
        that look like: C(5h34m56s), C(1m30s) etc. The supported units are C(us), C(ms), C(s), C(m) and C(h)."
      - Requires API version >= 1.25.
    type: dict
    suboptions:
      test:
        description:
          - Command to run to check health.
          - Must be either a string or a list. If it is a list, the first item must be one of C(NONE), C(CMD) or C(CMD-SHELL).
        type: raw
      interval:
        description:
          - Time between running the check.
        type: str
      timeout:
        description:
          - Maximum time to allow one check to run.
        type: str
      retries:
        description:
          - Consecutive failures needed to report unhealthy. It accept integer value.
        type: int
      start_period:
        description:
          - Start period for the container to initialize before starting health-retries countdown.
        type: str
    version_added: "2.8"
  hostname:
    description:
      - Container hostname.
      - Corresponds to the C(--hostname) option of C(docker service create).
      - Requires API version >= 1.25.
    type: str
  tty:
    description:
      - Allocate a pseudo-TTY.
      - Corresponds to the C(--tty) option of C(docker service create).
      - Requires API version >= 1.25.
    type: bool
  dns:
    description:
      - List of custom DNS servers.
      - Corresponds to the C(--dns) option of C(docker service create).
      - Requires API version >= 1.25.
    type: list
  dns_search:
    description:
      - List of custom DNS search domains.
      - Corresponds to the C(--dns-search) option of C(docker service create).
      - Requires API version >= 1.25.
    type: list
  dns_options:
    description:
      - List of custom DNS options.
      - Corresponds to the C(--dns-option) option of C(docker service create).
      - Requires API version >= 1.25.
    type: list
  force_update:
    description:
      - Force update even if no changes require it.
      - Corresponds to the C(--force) option of C(docker service update).
      - Requires API version >= 1.25.
    type: bool
    default: no
  groups:
    description:
      - List of additional group names and/or IDs that the container process will run as.
      - Corresponds to the C(--group) option of C(docker service update).
      - Requires API version >= 1.25.
    type: list
    version_added: "2.8"
  labels:
    description:
      - Dictionary of key value pairs.
      - Corresponds to the C(--label) option of C(docker service create).
    type: dict
  container_labels:
    description:
      - Dictionary of key value pairs.
      - Corresponds to the C(--container-label) option of C(docker service create).
    type: dict
  endpoint_mode:
    description:
      - Service endpoint mode.
      - Corresponds to the C(--endpoint-mode) option of C(docker service create).
      - Requires API version >= 1.25.
    type: str
    choices:
      - vip
      - dnsrr
  env:
    description:
      - List or dictionary of the service environment variables.
      - If passed a list each items need to be in the format of C(KEY=VALUE).
      - If passed a dictionary values which might be parsed as numbers,
        booleans or other types by the YAML parser must be quoted (e.g. C("true"))
        in order to avoid data loss.
      - Corresponds to the C(--env) option of C(docker service create).
    type: raw
  env_files:
    description:
      - List of paths to files, present on the target, containing environment variables C(FOO=BAR).
      - The order of the list is significant in determining the value assigned to a
        variable that shows up more than once.
      - If variable also present in I(env), then I(env) value will override.
    type: list
    version_added: "2.8"
  log_driver:
    description:
      - Configure the logging driver for a service.
      - Corresponds to the C(--log-driver) option of C(docker service create).
    type: str
  log_driver_options:
    description:
      - Options for service logging driver.
      - Corresponds to the C(--log-opt) option of C(docker service create).
    type: dict
  limit_cpu:
    description:
      - Service CPU limit. C(0) equals no limit.
      - Corresponds to the C(--limit-cpu) option of C(docker service create).
    type: float
  reserve_cpu:
    description:
      - Service CPU reservation. C(0) equals no reservation.
      - Corresponds to the C(--reserve-cpu) option of C(docker service create).
    type: float
  limit_memory:
    description:
      - "Service memory limit (format: C(<number>[<unit>])). Number is a positive integer.
        Unit can be C(B) (byte), C(K) (kibibyte, 1024B), C(M) (mebibyte), C(G) (gibibyte),
        C(T) (tebibyte), or C(P) (pebibyte)."
      - C(0) equals no limit.
      - Omitting the unit defaults to bytes.
      - Corresponds to the C(--limit-memory) option of C(docker service create).
    type: str
  reserve_memory:
    description:
      - "Service memory reservation (format: C(<number>[<unit>])). Number is a positive integer.
        Unit can be C(B) (byte), C(K) (kibibyte, 1024B), C(M) (mebibyte), C(G) (gibibyte),
        C(T) (tebibyte), or C(P) (pebibyte)."
      - C(0) equals no reservation.
      - Omitting the unit defaults to bytes.
      - Corresponds to the C(--reserve-memory) option of C(docker service create).
    type: str
  mode:
    description:
      - Service replication mode.
      - Corresponds to the C(--mode) option of C(docker service create).
    type: str
    default: replicated
  mounts:
    description:
      - List of dictionaries describing the service mounts.
      - Corresponds to the C(--mount) option of C(docker service create).
    type: list
    suboptions:
      source:
        description:
          - Mount source (e.g. a volume name or a host path).
        type: str
        required: yes
      target:
        description:
          - Container path.
        type: str
        required: yes
      type:
        description:
          - The mount type.
        type: str
        default: bind
        choices:
          - bind
          - volume
          - tmpfs
      readonly:
        description:
          - Whether the mount should be read-only.
        type: bool
        default: no
  secrets:
    description:
      - List of dictionaries describing the service secrets.
      - Corresponds to the C(--secret) option of C(docker service create).
      - Requires API version >= 1.25.
    type: list
    suboptions:
      secret_id:
        description:
          - Secret's ID.
        type: str
        required: yes
      secret_name:
        description:
          - Secret's name as defined at its creation.
        type: str
        required: yes
      filename:
        description:
          - Name of the file containing the secret. Defaults to the I(secret_name) if not specified.
        type: str
      uid:
        description:
          - UID of the secret file's owner.
        type: int
        default: 0
      gid:
        description:
          - GID of the secret file's group.
        type: int
        default: 0
      mode:
        description:
          - File access mode inside the container.
        type: int
        default: 0o444
  configs:
    description:
      - List of dictionaries describing the service configs.
      - Corresponds to the C(--config) option of C(docker service create).
      - Requires API version >= 1.30.
    type: list
    suboptions:
      config_id:
        description:
          - Config's ID.
        type: str
        required: yes
      config_name:
        description:
          - Config's name as defined at its creation.
        type: str
        required: yes
      filename:
        description:
          - Name of the file containing the config. Defaults to the I(config_name) if not specified.
        type: str
        required: yes
      uid:
        description:
          - UID of the config file's owner.
        type: int
        default: 0
      gid:
        description:
          - GID of the config file's group.
        type: int
        default: 0
      mode:
        description:
          - File access mode inside the container.
        type: str
        default: "0o444"
  networks:
    description:
      - List of the service networks names.
      - Corresponds to the C(--network) option of C(docker service create).
    type: list
  stop_signal:
    description:
      - Override default signal used to stop the container.
      - Corresponds to the C(--stop-signal) option of C(docker service create).
    type: str
    version_added: "2.8"
  publish:
    description:
      - List of dictionaries describing the service published ports.
      - Corresponds to the C(--publish) option of C(docker service create).
      - Requires API version >= 1.25.
    type: list
    suboptions:
      published_port:
        description:
          - The port to make externally available.
        type: int
        required: yes
      target_port:
        description:
          - The port inside the container to expose.
        type: int
        required: yes
      protocol:
        description:
          - What protocol to use.
        type: str
        default: tcp
        choices:
          - tcp
          - udp
      mode:
        description:
          - What publish mode to use.
          - Requires API version >= 1.32.
        type: str
        choices:
          - ingress
          - host
  replicas:
    description:
      - Number of containers instantiated in the service. Valid only if I(mode) is C(replicated).
      - If set to C(-1), and service is not present, service replicas will be set to C(1).
      - If set to C(-1), and service is present, service replicas will be unchanged.
      - Corresponds to the C(--replicas) option of C(docker service create).
    type: int
    default: -1
  restart_policy:
    description:
      - Restart condition of the service.
      - Corresponds to the C(--restart-condition) option of C(docker service create).
    type: str
    choices:
      - none
      - on-failure
      - any
  restart_policy_attempts:
    description:
      - Maximum number of service restarts.
      - Corresponds to the C(--restart-condition) option of C(docker service create).
    type: int
  restart_policy_delay:
    description:
      - Delay between restarts.
      - Corresponds to the C(--restart-delay) option of C(docker service create).
    type: int
  restart_policy_window:
    description:
      - Restart policy evaluation window.
      - Corresponds to the C(--restart-window) option of C(docker service create).
    type: int
  update_delay:
    description:
      - Rolling update delay in nanoseconds.
      - Corresponds to the C(--update-delay) option of C(docker service create).
      - Before Ansible 2.8, the default value for this option was C(10).
    type: int
  update_parallelism:
    description:
      - Rolling update parallelism.
      - Corresponds to the C(--update-parallelism) option of C(docker service create).
      - Before Ansible 2.8, the default value for this option was C(1).
    type: int
  update_failure_action:
    description:
      - Action to take in case of container failure.
      - Corresponds to the C(--update-failure-action) option of C(docker service create).
    type: str
    choices:
      - continue
      - pause
  update_monitor:
    description:
      - Time to monitor updated tasks for failures, in nanoseconds.
      - Corresponds to the C(--update-monitor) option of C(docker service create).
      - Requires API version >= 1.25.
    type: int
  update_max_failure_ratio:
    description:
      - Fraction of tasks that may fail during an update before the failure action is invoked.
      - Corresponds to the C(--update-max-failure-ratio) option of C(docker service create).
      - Requires API version >= 1.25.
    type: float
  update_order:
    description:
      - Specifies the order of operations when rolling out an updated task.
      - Corresponds to the C(--update-order) option of C(docker service create).
      - Requires API version >= 1.29.
    type: str
  user:
    description:
      - Sets the username or UID used for the specified command.
      - Before Ansible 2.8, the default value for this option was C(root).
      - The default has been removed so that the user defined in the image is used if no user is specified here.
      - Corresponds to the C(--user) option of C(docker service create).
    type: str
  working_dir:
    description:
      - Path to the working directory.
      - Corresponds to the C(--workdir) option of C(docker service create).
    type: str
    version_added: "2.8"
extends_documentation_fragment:
  - docker
  - docker.docker_py_2_documentation
requirements:
  - "docker >= 2.0"
  - "Docker API >= 1.24"
notes:
  - "Images will only resolve to the latest digest when using Docker API >= 1.30 and docker-py >= 3.2.0.
     When using older versions use C(force_update: true) to trigger the swarm to resolve a new image."
'''

RETURN = '''
ansible_swarm_service:
  returned: always
  type: dict
  description:
  - Dictionary of variables representing the current state of the service.
    Matches the module parameters format.
  - Note that facts are not part of registered vars but accessible directly.
  sample: '{
    "args": [
      "sleep",
      "3600"
    ],
    "constraints": [],
    "container_labels": {},
    "endpoint_mode": "vip",
    "env": [
      "ENVVAR1=envvar1"
    ],
    "force_update": False,
    "image": "alpine",
    "labels": {},
    "limit_cpu": 0.0,
    "limit_memory": 0,
    "log_driver": "json-file",
    "log_driver_options": {},
    "mode": "replicated",
    "mounts": [
      {
        "source": "/tmp/",
        "target": "/remote_tmp/",
        "type": "bind"
      }
    ],
    "secrets": [],
    "configs": [],
    "networks": [],
    "publish": [],
    "replicas": 1,
    "reserve_cpu": 0.0,
    "reserve_memory": 0,
    "restart_policy": "any",
    "restart_policy_attempts": 5,
    "restart_policy_delay": 0,
    "restart_policy_window": 30,
    "update_delay": 10,
    "update_parallelism": 1,
    "update_failure_action": "continue",
    "update_monitor": 5000000000
    "update_max_failure_ratio": 0,
    "update_order": "stop-first"
  }'
changes:
  returned: always
  description:
  - List of changed service attributes if a service has been altered,
    [] otherwise
  type: list
  sample: ['container_labels', 'replicas']
rebuilt:
  returned: always
  description:
  - True if the service has been recreated (removed and created)
  type: bool
  sample: True
'''

EXAMPLES = '''
- name: Set arguments
  docker_swarm_service:
    name: myservice
    image: alpine
    args:
      - "sleep"
      - "3600"

- name: Set a bind mount
  docker_swarm_service:
    name: myservice
    image: alpine
    mounts:
      - source: /tmp/
        target: /remote_tmp/
        type: bind

- name: Set environment variables
  docker_swarm_service:
    name: myservice
    image: alpine
    env:
      - "ENVVAR1=envvar1"
      - "ENVVAR2=envvar2"

- name: Set fluentd logging
  docker_swarm_service:
    name: myservice
    image: alpine
    log_driver: fluentd
    log_driver_options:
      fluentd-address: "127.0.0.1:24224"
      fluentd-async-connect: true
      tag: myservice

- name: Set restart policies
  docker_swarm_service:
    name: myservice
    image: alpine
    restart_policy: any
    restart_policy_attempts: 5
    restart_policy_delay: 5
    restart_policy_window: 30

- name: Set placement preferences
  docker_swarm_service:
    name: myservice
    image: alpine:edge
    placement_preferences:
      - spread: "node.labels.mylabel"

- name: Set configs
  docker_swarm_service:
    name: myservice
    image: alpine:edge
    configs:
      - config_id: myconfig_id
        config_name: myconfig_name
        filename: "/tmp/config.txt"

- name: Set networks
  docker_swarm_service:
    name: myservice
    image: alpine:edge
    networks:
      - mynetwork

- name: Set secrets
  docker_swarm_service:
    name: myservice
    image: alpine:edge
    secrets:
      - secret_id: mysecret_id
        secret_name: mysecret_name
        filename: "/run/secrets/secret.txt"

- name: Remove service
  docker_swarm_service:
    name: myservice
    state: absent

- name: Start service with healthcheck
  docker_swarm_service:
    name: myservice
    image: nginx:1.13
    healthcheck:
      # Check if nginx server is healthy by curl'ing the server.
      # If this fails or timeouts, the healthcheck fails.
      test: ["CMD", "curl", "--fail", "http://nginx.host.com"]
      interval: 1m30s
      timeout: 10s
      retries: 3
      start_period: 30s
'''

import shlex
import time
import operator

from distutils.version import LooseVersion

from ansible.module_utils.docker.common import (
    AnsibleDockerClient,
    DifferenceTracker,
    DockerBaseClass,
    convert_duration_to_nanosecond,
    parse_healthcheck

)
from ansible.module_utils.basic import human_to_bytes
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_text

try:
    from docker import types
    from docker.utils import (
        parse_repository_tag,
        parse_env_file,
        format_environment,
    )
    from docker.errors import (
        APIError,
        DockerException,
        NotFound,
    )
except ImportError:
    # missing docker-py handled in ansible.module_utils.docker.common
    pass


def get_docker_environment(env, env_files):
    """
    Will return a list of "KEY=VALUE" items. Supplied env variable can
    be either a list or a dictionary.

    If environment files are combined with explicit environment variables,
    the explicit environment variables take precedence.
    """
    env_dict = {}
    if env_files:
        for env_file in env_files:
            parsed_env_file = parse_env_file(env_file)
            for name, value in parsed_env_file.items():
                env_dict[name] = str(value)
    if env is not None and isinstance(env, string_types):
        env = env.split(',')
    if env is not None and isinstance(env, dict):
        for name, value in env.items():
            if not isinstance(value, string_types):
                raise ValueError(
                    'Non-string value found for env option. '
                    'Ambiguous env options must be wrapped in quotes to avoid YAML parsing. Key: %s' % name
                )
            env_dict[name] = str(value)
    elif env is not None and isinstance(env, list):
        for item in env:
            try:
                name, value = item.split('=', 1)
            except ValueError:
                raise ValueError('Invalid environment variable found in list, needs to be in format KEY=VALUE.')
            env_dict[name] = value
    elif env is not None:
        raise ValueError(
            'Invalid type for env %s (%s). Only list or dict allowed.' % (env, type(env))
        )
    env_list = format_environment(env_dict)
    if not env_list:
        if env is not None or env_files is not None:
            return []
        else:
            return None
    return sorted(env_list)


class DockerService(DockerBaseClass):
    def __init__(self):
        super(DockerService, self).__init__()
        self.image = ""
        self.command = None
        self.args = None
        self.endpoint_mode = None
        self.dns = None
        self.healthcheck = None
        self.healthcheck_disabled = None
        self.hostname = None
        self.tty = None
        self.dns_search = None
        self.dns_options = None
        self.env = None
        self.force_update = None
        self.groups = None
        self.log_driver = None
        self.log_driver_options = None
        self.labels = None
        self.container_labels = None
        self.limit_cpu = None
        self.limit_memory = None
        self.reserve_cpu = None
        self.reserve_memory = None
        self.mode = "replicated"
        self.user = None
        self.mounts = None
        self.configs = None
        self.secrets = None
        self.constraints = None
        self.networks = None
        self.stop_signal = None
        self.publish = None
        self.placement_preferences = None
        self.replicas = -1
        self.service_id = False
        self.service_version = False
        self.restart_policy = None
        self.restart_policy_attempts = None
        self.restart_policy_delay = None
        self.restart_policy_window = None
        self.update_delay = None
        self.update_parallelism = None
        self.update_failure_action = None
        self.update_monitor = None
        self.update_max_failure_ratio = None
        self.update_order = None
        self.working_dir = None

    def get_facts(self):
        return {
            'image': self.image,
            'mounts': self.mounts,
            'configs': self.configs,
            'networks': self.networks,
            'command': self.command,
            'args': self.args,
            'tty': self.tty,
            'dns': self.dns,
            'dns_search': self.dns_search,
            'dns_options': self.dns_options,
            'healthcheck': self.healthcheck,
            'healthcheck_disabled': self.healthcheck_disabled,
            'hostname': self.hostname,
            'env': self.env,
            'force_update': self.force_update,
            'groups': self.groups,
            'log_driver': self.log_driver,
            'log_driver_options': self.log_driver_options,
            'publish': self.publish,
            'constraints': self.constraints,
            'placement_preferences': self.placement_preferences,
            'labels': self.labels,
            'container_labels': self.container_labels,
            'mode': self.mode,
            'replicas': self.replicas,
            'endpoint_mode': self.endpoint_mode,
            'restart_policy': self.restart_policy,
            'stop_signal': self.stop_signal,
            'limit_cpu': self.limit_cpu,
            'limit_memory': self.limit_memory,
            'reserve_cpu': self.reserve_cpu,
            'reserve_memory': self.reserve_memory,
            'restart_policy_delay': self.restart_policy_delay,
            'restart_policy_attempts': self.restart_policy_attempts,
            'restart_policy_window': self.restart_policy_window,
            'update_delay': self.update_delay,
            'update_parallelism': self.update_parallelism,
            'update_failure_action': self.update_failure_action,
            'update_monitor': self.update_monitor,
            'update_max_failure_ratio': self.update_max_failure_ratio,
            'update_order': self.update_order,
            'working_dir': self.working_dir,
        }

    @staticmethod
    def from_ansible_params(ap, old_service, image_digest):
        s = DockerService()
        s.image = image_digest
        s.constraints = ap['constraints']
        s.placement_preferences = ap['placement_preferences']
        s.args = ap['args']
        s.endpoint_mode = ap['endpoint_mode']
        s.dns = ap['dns']
        s.dns_search = ap['dns_search']
        s.dns_options = ap['dns_options']
        s.healthcheck, s.healthcheck_disabled = parse_healthcheck(ap['healthcheck'])
        s.hostname = ap['hostname']
        s.tty = ap['tty']
        s.log_driver = ap['log_driver']
        s.log_driver_options = ap['log_driver_options']
        s.labels = ap['labels']
        s.container_labels = ap['container_labels']
        s.limit_cpu = ap['limit_cpu']
        s.reserve_cpu = ap['reserve_cpu']
        s.mode = ap['mode']
        s.networks = ap['networks']
        s.stop_signal = ap['stop_signal']
        s.restart_policy = ap['restart_policy']
        s.restart_policy_attempts = ap['restart_policy_attempts']
        s.restart_policy_delay = ap['restart_policy_delay']
        s.restart_policy_window = ap['restart_policy_window']
        s.update_delay = ap['update_delay']
        s.update_parallelism = ap['update_parallelism']
        s.update_failure_action = ap['update_failure_action']
        s.update_monitor = ap['update_monitor']
        s.update_max_failure_ratio = ap['update_max_failure_ratio']
        s.update_order = ap['update_order']
        s.user = ap['user']
        s.working_dir = ap['working_dir']

        s.command = ap['command']
        if isinstance(s.command, string_types):
            s.command = shlex.split(s.command)
        elif isinstance(s.command, list):
            invalid_items = [
                (index, item)
                for index, item in enumerate(s.command)
                if not isinstance(item, string_types)
            ]
            if invalid_items:
                errors = ', '.join(
                    [
                        '%s (%s) at index %s' % (item, type(item), index)
                        for index, item in invalid_items
                    ]
                )
                raise Exception(
                    'All items in a command list need to be strings. '
                    'Check quoting. Invalid items: %s.'
                    % errors
                )
            s.command = ap['command']
        elif s.command is not None:
            raise ValueError(
                'Invalid type for command %s (%s). '
                'Only string or list allowed. Check quoting.'
                % (s.command, type(s.command))
            )

        s.env = get_docker_environment(ap['env'], ap['env_files'])

        if ap['force_update']:
            s.force_update = int(str(time.time()).replace('.', ''))

        if ap['groups'] is not None:
            # In case integers are passed as groups, we need to convert them to
            # strings as docker internally treats them as strings.
            s.groups = [str(g) for g in ap['groups']]

        if ap['replicas'] == -1:
            if old_service:
                s.replicas = old_service.replicas
            else:
                s.replicas = 1
        else:
            s.replicas = ap['replicas']

        for param_name in ['reserve_memory', 'limit_memory']:
            if ap.get(param_name):
                try:
                    setattr(s, param_name, human_to_bytes(ap[param_name]))
                except ValueError as exc:
                    raise Exception('Failed to convert %s to bytes: %s' % (param_name, exc))

        if ap['publish'] is not None:
            s.publish = []
            for param_p in ap['publish']:
                service_p = {}
                service_p['protocol'] = param_p['protocol']
                service_p['mode'] = param_p['mode']
                service_p['published_port'] = param_p['published_port']
                service_p['target_port'] = param_p['target_port']
                s.publish.append(service_p)

        if ap['mounts'] is not None:
            s.mounts = []
            for param_m in ap['mounts']:
                service_m = {}
                service_m['readonly'] = param_m['readonly']
                service_m['type'] = param_m['type']
                service_m['source'] = param_m['source']
                service_m['target'] = param_m['target']
                s.mounts.append(service_m)

        if ap['configs'] is not None:
            s.configs = []
            for param_m in ap['configs']:
                service_c = {}
                service_c['config_id'] = param_m['config_id']
                service_c['config_name'] = param_m['config_name']
                service_c['filename'] = param_m['filename'] or service_c['config_name']
                service_c['uid'] = param_m['uid']
                service_c['gid'] = param_m['gid']
                service_c['mode'] = param_m['mode']
                s.configs.append(service_c)

        if ap['secrets'] is not None:
            s.secrets = []
            for param_m in ap['secrets']:
                service_s = {}
                service_s['secret_id'] = param_m['secret_id']
                service_s['secret_name'] = param_m['secret_name']
                service_s['filename'] = param_m['filename'] or service_s['secret_name']
                service_s['uid'] = param_m['uid']
                service_s['gid'] = param_m['gid']
                service_s['mode'] = param_m['mode']
                s.secrets.append(service_s)
        return s

    def compare(self, os):
        differences = DifferenceTracker()
        needs_rebuild = False
        force_update = False
        if self.endpoint_mode is not None and self.endpoint_mode != os.endpoint_mode:
            differences.add('endpoint_mode', parameter=self.endpoint_mode, active=os.endpoint_mode)
        if self.env is not None and self.env != (os.env or []):
            differences.add('env', parameter=self.env, active=os.env)
        if self.log_driver is not None and self.log_driver != os.log_driver:
            differences.add('log_driver', parameter=self.log_driver, active=os.log_driver)
        if self.log_driver_options is not None and self.log_driver_options != (os.log_driver_options or {}):
            differences.add('log_opt', parameter=self.log_driver_options, active=os.log_driver_options)
        if self.mode != os.mode:
            needs_rebuild = True
            differences.add('mode', parameter=self.mode, active=os.mode)
        if self.mounts is not None and self.mounts != (os.mounts or []):
            differences.add('mounts', parameter=self.mounts, active=os.mounts)
        if self.configs is not None and self.configs != (os.configs or []):
            differences.add('configs', parameter=self.configs, active=os.configs)
        if self.secrets is not None and self.secrets != (os.secrets or []):
            differences.add('secrets', parameter=self.secrets, active=os.secrets)
        if self.networks is not None and self.networks != (os.networks or []):
            differences.add('networks', parameter=self.networks, active=os.networks)
            needs_rebuild = True
        if self.replicas != os.replicas:
            differences.add('replicas', parameter=self.replicas, active=os.replicas)
        if self.command is not None and self.command != (os.command or []):
            differences.add('command', parameter=self.command, active=os.command)
        if self.args is not None and self.args != (os.args or []):
            differences.add('args', parameter=self.args, active=os.args)
        if self.constraints is not None and self.constraints != (os.constraints or []):
            differences.add('constraints', parameter=self.constraints, active=os.constraints)
        if self.placement_preferences is not None and self.placement_preferences != (os.placement_preferences or []):
            differences.add('placement_preferences', parameter=self.placement_preferences, active=os.placement_preferences)
        if self.groups is not None and self.groups != (os.groups or []):
            differences.add('groups', parameter=self.groups, active=os.groups)
        if self.labels is not None and self.labels != (os.labels or {}):
            differences.add('labels', parameter=self.labels, active=os.labels)
        if self.limit_cpu is not None and self.limit_cpu != os.limit_cpu:
            differences.add('limit_cpu', parameter=self.limit_cpu, active=os.limit_cpu)
        if self.limit_memory is not None and self.limit_memory != os.limit_memory:
            differences.add('limit_memory', parameter=self.limit_memory, active=os.limit_memory)
        if self.reserve_cpu is not None and self.reserve_cpu != os.reserve_cpu:
            differences.add('reserve_cpu', parameter=self.reserve_cpu, active=os.reserve_cpu)
        if self.reserve_memory is not None and self.reserve_memory != os.reserve_memory:
            differences.add('reserve_memory', parameter=self.reserve_memory, active=os.reserve_memory)
        if self.container_labels is not None and self.container_labels != (os.container_labels or {}):
            differences.add('container_labels', parameter=self.container_labels, active=os.container_labels)
        if self.stop_signal is not None and self.stop_signal != os.stop_signal:
            differences.add('stop_signal', parameter=self.stop_signal, active=os.stop_signal)
        if self.has_publish_changed(os.publish):
            differences.add('publish', parameter=self.publish, active=os.publish)
        if self.restart_policy is not None and self.restart_policy != os.restart_policy:
            differences.add('restart_policy', parameter=self.restart_policy, active=os.restart_policy)
        if self.restart_policy_attempts is not None and self.restart_policy_attempts != os.restart_policy_attempts:
            differences.add('restart_policy_attempts', parameter=self.restart_policy_attempts, active=os.restart_policy_attempts)
        if self.restart_policy_delay is not None and self.restart_policy_delay != os.restart_policy_delay:
            differences.add('restart_policy_delay', parameter=self.restart_policy_delay, active=os.restart_policy_delay)
        if self.restart_policy_window is not None and self.restart_policy_window != os.restart_policy_window:
            differences.add('restart_policy_window', parameter=self.restart_policy_window, active=os.restart_policy_window)
        if self.update_delay is not None and self.update_delay != os.update_delay:
            differences.add('update_delay', parameter=self.update_delay, active=os.update_delay)
        if self.update_parallelism is not None and self.update_parallelism != os.update_parallelism:
            differences.add('update_parallelism', parameter=self.update_parallelism, active=os.update_parallelism)
        if self.update_failure_action is not None and self.update_failure_action != os.update_failure_action:
            differences.add('update_failure_action', parameter=self.update_failure_action, active=os.update_failure_action)
        if self.update_monitor is not None and self.update_monitor != os.update_monitor:
            differences.add('update_monitor', parameter=self.update_monitor, active=os.update_monitor)
        if self.update_max_failure_ratio is not None and self.update_max_failure_ratio != os.update_max_failure_ratio:
            differences.add('update_max_failure_ratio', parameter=self.update_max_failure_ratio, active=os.update_max_failure_ratio)
        if self.update_order is not None and self.update_order != os.update_order:
            differences.add('update_order', parameter=self.update_order, active=os.update_order)
        has_image_changed, change = self.has_image_changed(os.image)
        if has_image_changed:
            differences.add('image', parameter=self.image, active=change)
        if self.user and self.user != os.user:
            differences.add('user', parameter=self.user, active=os.user)
        if self.dns is not None and self.dns != (os.dns or []):
            differences.add('dns', parameter=self.dns, active=os.dns)
        if self.dns_search is not None and self.dns_search != (os.dns_search or []):
            differences.add('dns_search', parameter=self.dns_search, active=os.dns_search)
        if self.dns_options is not None and self.dns_options != (os.dns_options or []):
            differences.add('dns_options', parameter=self.dns_options, active=os.dns_options)
        if self.has_healthcheck_changed(os):
            differences.add('healthcheck', parameter=self.healthcheck, active=os.healthcheck)
        if self.hostname is not None and self.hostname != os.hostname:
            differences.add('hostname', parameter=self.hostname, active=os.hostname)
        if self.tty is not None and self.tty != os.tty:
            differences.add('tty', parameter=self.tty, active=os.tty)
        if self.working_dir is not None and self.working_dir != os.working_dir:
            differences.add('working_dir', parameter=self.working_dir, active=os.working_dir)
        if self.force_update:
            force_update = True
        return not differences.empty or force_update, differences, needs_rebuild, force_update

    def has_healthcheck_changed(self, old_publish):
        if self.healthcheck_disabled is False and self.healthcheck is None:
            return False
        if self.healthcheck_disabled and old_publish.healthcheck is None:
            return False
        return self.healthcheck != old_publish.healthcheck

    def has_publish_changed(self, old_publish):
        if self.publish is None:
            return False
        old_publish = old_publish or []
        if len(self.publish) != len(old_publish):
            return True
        publish_sorter = operator.itemgetter('published_port', 'target_port', 'protocol')
        publish = sorted(self.publish, key=publish_sorter)
        old_publish = sorted(old_publish, key=publish_sorter)
        for publish_item, old_publish_item in zip(publish, old_publish):
            ignored_keys = set()
            if not publish_item.get('mode'):
                ignored_keys.add('mode')
            # Create copies of publish_item dicts where keys specified in ignored_keys are left out
            filtered_old_publish_item = dict(
                (k, v) for k, v in old_publish_item.items() if k not in ignored_keys
            )
            filtered_publish_item = dict(
                (k, v) for k, v in publish_item.items() if k not in ignored_keys
            )
            if filtered_publish_item != filtered_old_publish_item:
                return True
        return False

    def has_image_changed(self, old_image):
        if '@' not in self.image:
            old_image = old_image.split('@')[0]
        return self.image != old_image, old_image

    def __str__(self):
        return str({
            'mode': self.mode,
            'env': self.env,
            'endpoint_mode': self.endpoint_mode,
            'mounts': self.mounts,
            'configs': self.configs,
            'secrets': self.secrets,
            'networks': self.networks,
            'replicas': self.replicas
        })

    def build_container_spec(self):
        mounts = None
        if self.mounts is not None:
            mounts = []
            for mount_config in self.mounts:
                mounts.append(
                    types.Mount(
                        target=mount_config['target'],
                        source=mount_config['source'],
                        type=mount_config['type'],
                        read_only=mount_config['readonly']
                    )
                )

        configs = None
        if self.configs is not None:
            configs = []
            for config_config in self.configs:
                configs.append(
                    types.ConfigReference(
                        config_id=config_config['config_id'],
                        config_name=config_config['config_name'],
                        filename=config_config.get('filename'),
                        uid=config_config.get('uid'),
                        gid=config_config.get('gid'),
                        mode=config_config.get('mode')
                    )
                )

        secrets = None
        if self.secrets is not None:
            secrets = []
            for secret_config in self.secrets:
                secrets.append(
                    types.SecretReference(
                        secret_id=secret_config['secret_id'],
                        secret_name=secret_config['secret_name'],
                        filename=secret_config.get('filename'),
                        uid=secret_config.get('uid'),
                        gid=secret_config.get('gid'),
                        mode=secret_config.get('mode')
                    )
                )

        dns_config_args = {}
        if self.dns is not None:
            dns_config_args['nameservers'] = self.dns
        if self.dns_search is not None:
            dns_config_args['search'] = self.dns_search
        if self.dns_options is not None:
            dns_config_args['options'] = self.dns_options
        dns_config = types.DNSConfig(**dns_config_args) if dns_config_args else None

        container_spec_args = {}
        if self.command is not None:
            container_spec_args['command'] = self.command
        if self.args is not None:
            container_spec_args['args'] = self.args
        if self.env is not None:
            container_spec_args['env'] = self.env
        if self.user is not None:
            container_spec_args['user'] = self.user
        if self.container_labels is not None:
            container_spec_args['labels'] = self.container_labels
        if self.healthcheck is not None:
            container_spec_args['healthcheck'] = types.Healthcheck(**self.healthcheck)
        if self.hostname is not None:
            container_spec_args['hostname'] = self.hostname
        if self.stop_signal is not None:
            container_spec_args['stop_signal'] = self.stop_signal
        if self.tty is not None:
            container_spec_args['tty'] = self.tty
        if self.groups is not None:
            container_spec_args['groups'] = self.groups
        if self.working_dir is not None:
            container_spec_args['workdir'] = self.working_dir
        if secrets is not None:
            container_spec_args['secrets'] = secrets
        if mounts is not None:
            container_spec_args['mounts'] = mounts
        if dns_config is not None:
            container_spec_args['dns_config'] = dns_config
        if configs is not None:
            container_spec_args['configs'] = configs

        return types.ContainerSpec(self.image, **container_spec_args)

    def build_placement(self):
        placement_args = {}
        if self.constraints is not None:
            placement_args['constraints'] = self.constraints
        if self.placement_preferences is not None:
            placement_args['preferences'] = [
                {key.title(): {'SpreadDescriptor': value}}
                for preference in self.placement_preferences
                for key, value in preference.items()
            ]
        return types.Placement(**placement_args) if placement_args else None

    def build_update_config(self):
        update_config_args = {}
        if self.update_parallelism is not None:
            update_config_args['parallelism'] = self.update_parallelism
        if self.update_delay is not None:
            update_config_args['delay'] = self.update_delay
        if self.update_failure_action is not None:
            update_config_args['failure_action'] = self.update_failure_action
        if self.update_monitor is not None:
            update_config_args['monitor'] = self.update_monitor
        if self.update_max_failure_ratio is not None:
            update_config_args['max_failure_ratio'] = self.update_max_failure_ratio
        if self.update_order is not None:
            update_config_args['order'] = self.update_order
        return types.UpdateConfig(**update_config_args) if update_config_args else None

    def build_log_driver(self):
        log_driver_args = {}
        if self.log_driver is not None:
            log_driver_args['name'] = self.log_driver
        if self.log_driver_options is not None:
            log_driver_args['options'] = self.log_driver_options
        return types.DriverConfig(**log_driver_args) if log_driver_args else None

    def build_restart_policy(self):
        restart_policy_args = {}
        if self.restart_policy is not None:
            restart_policy_args['condition'] = self.restart_policy
        if self.restart_policy_delay is not None:
            restart_policy_args['delay'] = self.restart_policy_delay
        if self.restart_policy_attempts is not None:
            restart_policy_args['max_attempts'] = self.restart_policy_attempts
        if self.restart_policy_window is not None:
            restart_policy_args['window'] = self.restart_policy_window
        return types.RestartPolicy(**restart_policy_args) if restart_policy_args else None

    def build_resources(self):
        resources_args = {}
        if self.limit_cpu is not None:
            resources_args['cpu_limit'] = int(self.limit_cpu * 1000000000.0)
        if self.limit_memory is not None:
            resources_args['mem_limit'] = self.limit_memory
        if self.reserve_cpu is not None:
            resources_args['cpu_reservation'] = int(self.reserve_cpu * 1000000000.0)
        if self.reserve_memory is not None:
            resources_args['mem_reservation'] = self.reserve_memory
        return types.Resources(**resources_args) if resources_args else None

    def build_task_template(self, container_spec, placement=None):
        log_driver = self.build_log_driver()
        restart_policy = self.build_restart_policy()
        resources = self.build_resources()

        task_template_args = {}
        if placement is not None:
            task_template_args['placement'] = placement
        if log_driver is not None:
            task_template_args['log_driver'] = log_driver
        if restart_policy is not None:
            task_template_args['restart_policy'] = restart_policy
        if resources is not None:
            task_template_args['resources'] = resources
        if self.force_update:
            task_template_args['force_update'] = self.force_update
        return types.TaskTemplate(container_spec=container_spec, **task_template_args)

    def build_service_mode(self):
        if self.mode == 'global':
            self.replicas = None
        return types.ServiceMode(self.mode, replicas=self.replicas)

    def build_networks(self, docker_networks):
        networks = None
        if self.networks is not None:
            networks = []
            for network_name in self.networks:
                network_id = None
                try:
                    network_id = list(
                        filter(lambda n: n['name'] == network_name, docker_networks)
                    )[0]['id']
                except (IndexError, KeyError):
                    pass
                if network_id:
                    networks.append({'Target': network_id})
                else:
                    raise Exception('no docker networks named: %s' % network_name)
        return networks

    def build_endpoint_spec(self):
        endpoint_spec_args = {}
        if self.publish is not None:
            ports = {}
            for port in self.publish:
                if port.get('mode'):
                    ports[int(port['published_port'])] = (
                        int(port['target_port']),
                        port['protocol'],
                        port['mode'],
                    )
                else:
                    ports[int(port['published_port'])] = (
                        int(port['target_port']),
                        port['protocol'],
                    )
            endpoint_spec_args['ports'] = ports
        if self.endpoint_mode is not None:
            endpoint_spec_args['mode'] = self.endpoint_mode
        return types.EndpointSpec(**endpoint_spec_args) if endpoint_spec_args else None

    def build_docker_service(self, docker_networks):
        container_spec = self.build_container_spec()
        placement = self.build_placement()
        task_template = self.build_task_template(container_spec, placement)

        update_config = self.build_update_config()
        service_mode = self.build_service_mode()
        networks = self.build_networks(docker_networks)
        endpoint_spec = self.build_endpoint_spec()

        service = {'task_template': task_template, 'mode': service_mode}
        if update_config:
            service['update_config'] = update_config
        if networks:
            service['networks'] = networks
        if endpoint_spec:
            service['endpoint_spec'] = endpoint_spec
        if self.labels:
            service['labels'] = self.labels
        return service


class DockerServiceManager(object):

    def __init__(self, client):
        self.client = client
        self.retries = 2
        self.diff_tracker = None

    def get_networks_names_ids(self):
        return [{'name': n['Name'], 'id': n['Id']} for n in self.client.networks()]

    def get_service(self, name):
        try:
            raw_data = self.client.inspect_service(name)
        except NotFound:
            return None
        ds = DockerService()

        task_template_data = raw_data['Spec']['TaskTemplate']
        ds.image = task_template_data['ContainerSpec']['Image']
        ds.user = task_template_data['ContainerSpec'].get('User')
        ds.env = task_template_data['ContainerSpec'].get('Env')
        ds.command = task_template_data['ContainerSpec'].get('Command')
        ds.args = task_template_data['ContainerSpec'].get('Args')
        ds.groups = task_template_data['ContainerSpec'].get('Groups')
        ds.stop_signal = task_template_data['ContainerSpec'].get('StopSignal')
        ds.working_dir = task_template_data['ContainerSpec'].get('Dir')

        healthcheck_data = task_template_data['ContainerSpec'].get('Healthcheck')
        if healthcheck_data:
            options = ['test', 'interval', 'timeout', 'start_period', 'retries']
            healthcheck = dict(
                (key.lower(), value) for key, value in healthcheck_data.items()
                if value is not None and key.lower() in options
            )
            ds.healthcheck = healthcheck

        update_config_data = raw_data['Spec'].get('UpdateConfig')
        if update_config_data:
            ds.update_delay = update_config_data.get('Delay')
            ds.update_parallelism = update_config_data.get('Parallelism')
            ds.update_failure_action = update_config_data.get('FailureAction')
            ds.update_monitor = update_config_data.get('Monitor')
            ds.update_max_failure_ratio = update_config_data.get('MaxFailureRatio')
            ds.update_order = update_config_data.get('Order')

        dns_config = task_template_data['ContainerSpec'].get('DNSConfig')
        if dns_config:
            ds.dns = dns_config.get('Nameservers')
            ds.dns_search = dns_config.get('Search')
            ds.dns_options = dns_config.get('Options')

        ds.hostname = task_template_data['ContainerSpec'].get('Hostname')
        ds.tty = task_template_data['ContainerSpec'].get('TTY')

        placement = task_template_data.get('Placement')
        if placement:
            ds.constraints = placement.get('Constraints')
            placement_preferences = []
            for preference in placement.get('Preferences', []):
                placement_preferences.append(
                    dict(
                        (key.lower(), value['SpreadDescriptor'])
                        for key, value in preference.items()
                    )
                )
            ds.placement_preferences = placement_preferences or None

        restart_policy_data = task_template_data.get('RestartPolicy')
        if restart_policy_data:
            ds.restart_policy = restart_policy_data.get('Condition')
            ds.restart_policy_delay = restart_policy_data.get('Delay')
            ds.restart_policy_attempts = restart_policy_data.get('MaxAttempts')
            ds.restart_policy_window = restart_policy_data.get('Window')

        raw_data_endpoint_spec = raw_data['Spec'].get('EndpointSpec')
        if raw_data_endpoint_spec:
            ds.endpoint_mode = raw_data_endpoint_spec.get('Mode')
            raw_data_ports = raw_data_endpoint_spec.get('Ports')
            if raw_data_ports:
                ds.publish = []
                for port in raw_data_ports:
                    ds.publish.append({
                        'protocol': port['Protocol'],
                        'mode': port.get('PublishMode', None),
                        'published_port': int(port['PublishedPort']),
                        'target_port': int(port['TargetPort'])
                    })

        raw_data_limits = task_template_data.get('Resources', {}).get('Limits')
        if raw_data_limits:
            raw_cpu_limits = raw_data_limits.get('NanoCPUs')
            if raw_cpu_limits:
                ds.limit_cpu = float(raw_cpu_limits) / 1000000000

            raw_memory_limits = raw_data_limits.get('MemoryBytes')
            if raw_memory_limits:
                ds.limit_memory = int(raw_memory_limits)

        raw_data_reservations = task_template_data.get('Resources', {}).get('Reservations')
        if raw_data_reservations:
            raw_cpu_reservations = raw_data_reservations.get('NanoCPUs')
            if raw_cpu_reservations:
                ds.reserve_cpu = float(raw_cpu_reservations) / 1000000000

            raw_memory_reservations = raw_data_reservations.get('MemoryBytes')
            if raw_memory_reservations:
                ds.reserve_memory = int(raw_memory_reservations)

        ds.labels = raw_data['Spec'].get('Labels')
        ds.log_driver = task_template_data.get('LogDriver', {}).get('Name')
        ds.log_driver_options = task_template_data.get('LogDriver', {}).get('Options')
        ds.container_labels = task_template_data['ContainerSpec'].get('Labels')

        mode = raw_data['Spec']['Mode']
        if 'Replicated' in mode.keys():
            ds.mode = to_text('replicated', encoding='utf-8')
            ds.replicas = mode['Replicated']['Replicas']
        elif 'Global' in mode.keys():
            ds.mode = 'global'
        else:
            raise Exception('Unknown service mode: %s' % mode)

        raw_data_mounts = task_template_data['ContainerSpec'].get('Mounts')
        if raw_data_mounts:
            ds.mounts = []
            for mount_data in raw_data_mounts:
                ds.mounts.append({
                    'source': mount_data['Source'],
                    'type': mount_data['Type'],
                    'target': mount_data['Target'],
                    'readonly': mount_data.get('ReadOnly', False)
                })

        raw_data_configs = task_template_data['ContainerSpec'].get('Configs')
        if raw_data_configs:
            ds.configs = []
            for config_data in raw_data_configs:
                ds.configs.append({
                    'config_id': config_data['ConfigID'],
                    'config_name': config_data['ConfigName'],
                    'filename': config_data['File'].get('Name'),
                    'uid': int(config_data['File'].get('UID')),
                    'gid': int(config_data['File'].get('GID')),
                    'mode': config_data['File'].get('Mode')
                })

        raw_data_secrets = task_template_data['ContainerSpec'].get('Secrets')
        if raw_data_secrets:
            ds.secrets = []
            for secret_data in raw_data_secrets:
                ds.secrets.append({
                    'secret_id': secret_data['SecretID'],
                    'secret_name': secret_data['SecretName'],
                    'filename': secret_data['File'].get('Name'),
                    'uid': int(secret_data['File'].get('UID')),
                    'gid': int(secret_data['File'].get('GID')),
                    'mode': secret_data['File'].get('Mode')
                })

        networks_names_ids = self.get_networks_names_ids()
        raw_networks_data = task_template_data.get('Networks', raw_data['Spec'].get('Networks'))
        if raw_networks_data:
            ds.networks = []
            for network_data in raw_networks_data:
                network_name = [network_name_id['name'] for network_name_id in networks_names_ids if
                                network_name_id['id'] == network_data['Target']]
                if len(network_name) == 0:
                    ds.networks.append(network_data['Target'])
                else:
                    ds.networks.append(network_name[0])

        ds.service_version = raw_data['Version']['Index']
        ds.service_id = raw_data['ID']
        return ds

    def update_service(self, name, old_service, new_service):
        service_data = new_service.build_docker_service(self.get_networks_names_ids())
        self.client.update_service(
            old_service.service_id,
            old_service.service_version,
            name=name,
            **service_data
        )

    def create_service(self, name, service):
        service_data = service.build_docker_service(self.get_networks_names_ids())
        self.client.create_service(name=name, **service_data)

    def remove_service(self, name):
        self.client.remove_service(name)

    def get_image_digest(self, name, resolve=True):
        if (
            not name
            or not resolve
            or self.client.docker_py_version < LooseVersion('3.2')
            or self.client.docker_api_version < LooseVersion('1.30')
        ):
            return name
        repo, tag = parse_repository_tag(name)
        if not tag:
            tag = 'latest'
        name = repo + ':' + tag
        distribution_data = self.client.inspect_distribution(name)
        digest = distribution_data['Descriptor']['digest']
        return '%s@%s' % (name, digest)

    def run(self):
        self.diff_tracker = DifferenceTracker()
        module = self.client.module

        image = module.params['image']
        try:
            image_digest = self.get_image_digest(
                name=image,
                resolve=module.params['resolve_image']
            )
        except DockerException as e:
            self.client.fail(
                "Error looking for an image named %s: %s" % (image, e))
        try:
            current_service = self.get_service(module.params['name'])
        except Exception as e:
            self.client.fail(
                "Error looking for service named %s: %s" % (module.params['name'], e))
        try:
            new_service = DockerService.from_ansible_params(
                module.params,
                current_service,
                image_digest
            )
        except Exception as e:
            self.client.fail(
                "Error parsing module parameters: %s" % e)

        changed = False
        msg = 'noop'
        rebuilt = False
        differences = DifferenceTracker()
        facts = {}

        if current_service:
            if module.params['state'] == 'absent':
                if not module.check_mode:
                    self.remove_service(module.params['name'])
                msg = 'Service removed'
                changed = True
            else:
                changed, differences, need_rebuild, force_update = new_service.compare(current_service)
                if changed:
                    self.diff_tracker.merge(differences)
                    if need_rebuild:
                        if not module.check_mode:
                            self.remove_service(module.params['name'])
                            self.create_service(
                                module.params['name'],
                                new_service
                            )
                        msg = 'Service rebuilt'
                        rebuilt = True
                    else:
                        if not module.check_mode:
                            self.update_service(
                                module.params['name'],
                                current_service,
                                new_service
                            )
                        msg = 'Service updated'
                        rebuilt = False
                else:
                    if force_update:
                        if not module.check_mode:
                            self.update_service(
                                module.params['name'],
                                current_service,
                                new_service
                            )
                        msg = 'Service forcefully updated'
                        rebuilt = False
                        changed = True
                    else:
                        msg = 'Service unchanged'
                facts = new_service.get_facts()
        else:
            if module.params['state'] == 'absent':
                msg = 'Service absent'
            else:
                if not module.check_mode:
                    self.create_service(module.params['name'], new_service)
                msg = 'Service created'
                changed = True
                facts = new_service.get_facts()

        return msg, changed, rebuilt, differences.get_legacy_docker_diffs(), facts

    def run_safe(self):
        while True:
            try:
                return self.run()
            except APIError as e:
                # Sometimes Version.Index will have changed between an inspect and
                # update. If this is encountered we'll retry the update.
                if self.retries > 0 and 'update out of sequence' in str(e.explanation):
                    self.retries -= 1
                    time.sleep(1)
                else:
                    raise


def _detect_publish_mode_usage(client):
    for publish_def in client.module.params['publish']:
        if publish_def.get('mode'):
            return True
    return False


def _detect_healthcheck_start_period(client):
    return client.module.params['healthcheck']['start_period'] is not None


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        image=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        mounts=dict(type='list', elements='dict', options=dict(
            source=dict(type='str', required=True),
            target=dict(type='str', required=True),
            type=dict(
                type='str',
                default='bind',
                choices=['bind', 'volume', 'tmpfs']
            ),
            readonly=dict(type='bool', default=False),
        )),
        configs=dict(type='list', elements='dict', options=dict(
            config_id=dict(type='str', required=True),
            config_name=dict(type='str', required=True),
            filename=dict(type='str'),
            uid=dict(type='int', default=0),
            gid=dict(type='int', default=0),
            mode=dict(type='int', default=0o444),
        )),
        secrets=dict(type='list', elements='dict', options=dict(
            secret_id=dict(type='str', required=True),
            secret_name=dict(type='str', required=True),
            filename=dict(type='str'),
            uid=dict(type='int', default=0),
            gid=dict(type='int', default=0),
            mode=dict(type='int', default=0o444),
        )),
        networks=dict(type='list', elements='str'),
        command=dict(type='raw'),
        args=dict(type='list', elements='str'),
        env=dict(type='raw'),
        env_files=dict(type='list', elements='path'),
        force_update=dict(type='bool', default=False),
        groups=dict(type='list', elements='str'),
        log_driver=dict(type='str'),
        log_driver_options=dict(type='dict'),
        publish=dict(type='list', elements='dict', options=dict(
            published_port=dict(type='int', required=True),
            target_port=dict(type='int', required=True),
            protocol=dict(type='str', default='tcp', choices=('tcp', 'udp')),
            mode=dict(type='str', choices=('ingress', 'host')),
        )),
        constraints=dict(type='list'),
        placement_preferences=dict(type='list'),
        tty=dict(type='bool'),
        dns=dict(type='list'),
        dns_search=dict(type='list'),
        dns_options=dict(type='list'),
        healthcheck=dict(type='dict', options=dict(
            test=dict(type='raw'),
            interval=dict(type='str'),
            timeout=dict(type='str'),
            start_period=dict(type='str'),
            retries=dict(type='int'),
        )),
        hostname=dict(type='str'),
        labels=dict(type='dict'),
        container_labels=dict(type='dict'),
        mode=dict(type='str', default='replicated'),
        replicas=dict(type='int', default=-1),
        endpoint_mode=dict(type='str', choices=['vip', 'dnsrr']),
        stop_signal=dict(type='str'),
        limit_cpu=dict(type='float'),
        limit_memory=dict(type='str'),
        reserve_cpu=dict(type='float'),
        reserve_memory=dict(type='str'),
        resolve_image=dict(type='bool', default=True),
        restart_policy=dict(type='str', choices=['none', 'on-failure', 'any']),
        restart_policy_delay=dict(type='int'),
        restart_policy_attempts=dict(type='int'),
        restart_policy_window=dict(type='int'),
        update_delay=dict(type='int'),
        update_parallelism=dict(type='int'),
        update_failure_action=dict(type='str', choices=['continue', 'pause']),
        update_monitor=dict(type='int'),
        update_max_failure_ratio=dict(type='float'),
        update_order=dict(type='str'),
        user=dict(type='str'),
        working_dir=dict(type='str'),
    )

    option_minimal_versions = dict(
        dns=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        dns_options=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        dns_search=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        endpoint_mode=dict(docker_py_version='3.0.0', docker_api_version='1.25'),
        force_update=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        healthcheck=dict(docker_py_version='2.0.0', docker_api_version='1.25'),
        hostname=dict(docker_py_version='2.2.0', docker_api_version='1.25'),
        groups=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        tty=dict(docker_py_version='2.4.0', docker_api_version='1.25'),
        secrets=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        configs=dict(docker_py_version='2.6.0', docker_api_version='1.30'),
        update_max_failure_ratio=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        update_monitor=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        update_order=dict(docker_py_version='2.7.0', docker_api_version='1.29'),
        stop_signal=dict(docker_py_version='2.6.0', docker_api_version='1.28'),
        placement_preferences=dict(docker_py_version='2.4.0', docker_api_version='1.27'),
        publish=dict(docker_py_version='3.0.0', docker_api_version='1.25'),
        # specials
        publish_mode=dict(
            docker_py_version='3.0.0',
            docker_api_version='1.25',
            detect_usage=_detect_publish_mode_usage,
            usage_msg='set publish.mode'
        ),
        healthcheck_start_period=dict(
            docker_py_version='2.4.0',
            docker_api_version='1.25',
            detect_usage=_detect_healthcheck_start_period,
            usage_msg='set healthcheck.start_period'
        )
    )

    required_if = [
        ('state', 'present', ['image'])
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
        min_docker_version='2.0.0',
        min_docker_api_version='1.24',
        option_minimal_versions=option_minimal_versions,
    )

    dsm = DockerServiceManager(client)
    msg, changed, rebuilt, changes, facts = dsm.run_safe()

    results = dict(
        msg=msg,
        changed=changed,
        rebuilt=rebuilt,
        changes=changes,
        ansible_docker_service=facts,
    )
    if client.module._diff:
        before, after = dsm.diff_tracker.get_before_after()
        results['diff'] = dict(before=before, after=after)

    client.module.exit_json(**results)


if __name__ == '__main__':
    main()
