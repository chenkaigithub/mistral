# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Configuration options registration and useful routines.
"""

from oslo.config import cfg

from mistral.openstack.common import log
from mistral import version

api_opts = [
    cfg.StrOpt('host', default='0.0.0.0', help='Mistral API server host'),
    cfg.IntOpt('port', default=8989, help='Mistral API server port')
]

engine_opts = [
    cfg.StrOpt('engine', default='default',
               help='Mistral engine plugin'),
    cfg.StrOpt('host', default='0.0.0.0',
               help='Name of the engine node. This can be an opaque '
                    'identifier. It is not necessarily a hostname, '
                    'FQDN, or IP address.'),
    cfg.StrOpt('topic', default='engine',
               help='The message topic that the engine listens on.'),
    cfg.StrOpt('version', default='1.0',
               help='The version of the engine.')
]

pecan_opts = [
    cfg.StrOpt('root', default='mistral.api.controllers.root.RootController',
               help='Pecan root controller'),
    cfg.ListOpt('modules', default=["mistral.api"],
                help='A list of modules where pecan will search for '
                     'applications.'),
    cfg.BoolOpt('debug', default=False,
                help='Enables the ability to display tracebacks in the '
                     'browser and interactively debug during '
                     'development.'),
    cfg.BoolOpt('auth_enable', default=True,
                help='Enables user authentication in pecan.')
]

db_opts = [
    # TODO: add DB properties.
]

use_debugger = cfg.BoolOpt(
    "use-debugger",
    default=False,
    help='Enables debugger. Note that using this option changes how the '
    'eventlet library is used to support async IO. This could result '
    'in failures that do not occur under normal operation. '
    'Use at your own risk.'
)

executor_opts = [
    cfg.StrOpt('host', default='0.0.0.0',
               help='Name of the executor node. This can be an opaque '
                    'identifier. It is not necessarily a hostname, '
                    'FQDN, or IP address.'),
    cfg.StrOpt('topic', default='executor',
               help='The message topic that the executor listens on.'),
    cfg.StrOpt('version', default='1.0',
               help='The version of the executor.')
]

launch_opt = cfg.ListOpt(
    'server',
    default=['all'],
    help='Specifies which mistral server to start by the launch script. '
         'Valid options are all or any combination of '
         'api, engine, and executor.'
)

action_plugins_opt = cfg.ListOpt(
    'action_plugins',
    default=['mistral.actions.std'],
    help='List of namespaces to search for plug-ins.')


wf_trace_log_name_opt = cfg.StrOpt('workflow_trace_log_name',
                                   default='workflow_trace',
                                   help='Logger name for pretty '
                                   'workflow trace output.')

CONF = cfg.CONF

CONF.register_opts(api_opts, group='api')
CONF.register_opts(engine_opts, group='engine')
CONF.register_opts(pecan_opts, group='pecan')
CONF.register_opts(db_opts, group='database')
CONF.register_opts(executor_opts, group='executor')
CONF.register_opt(wf_trace_log_name_opt)
CONF.register_opt(action_plugins_opt)

CONF.register_cli_opt(use_debugger)
CONF.register_cli_opt(launch_opt)

CONF.import_opt('verbose', 'mistral.openstack.common.log')
CONF.import_opt('debug', 'mistral.openstack.common.log')
CONF.import_opt('log_dir', 'mistral.openstack.common.log')
CONF.import_opt('log_file', 'mistral.openstack.common.log')
CONF.import_opt('log_config_append', 'mistral.openstack.common.log')
CONF.import_opt('log_format', 'mistral.openstack.common.log')
CONF.import_opt('log_date_format', 'mistral.openstack.common.log')
CONF.import_opt('use_syslog', 'mistral.openstack.common.log')
CONF.import_opt('syslog_log_facility', 'mistral.openstack.common.log')

cfg.set_defaults(log.log_opts,
                 default_log_levels=['sqlalchemy=WARN',
                                     'eventlet.wsgi.server=WARN'])


def parse_args(args=None, usage=None, default_config_files=None):
    CONF(args=args,
         project='mistral',
         version=version,
         usage=usage,
         default_config_files=default_config_files)
