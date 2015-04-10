# Copyright 2015 - StackStorm, Inc.
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

import copy

import yaml

from mistral import exceptions as exc
from mistral.openstack.common import log as logging
from mistral.tests.unit.workbook.v2 import base
from mistral import utils
from mistral.workbook.v2 import tasks


LOG = logging.getLogger(__name__)


class WorkflowSpecValidation(base.WorkflowSpecValidationTestCase):

    def test_workflow_types(self):
        tests = [
            ({'type': 'direct'}, False),
            ({'type': 'reverse'}, False),
            ({'type': 'circular'}, True),
            ({'type': None}, True)
        ]

        for wf_type, expect_error in tests:
            overlay = {'test': wf_type}
            self._parse_dsl_spec(add_tasks=True,
                                 changes=overlay,
                                 expect_error=expect_error)

    def test_direct_workflow(self):
        overlay = {'test': {'type': 'direct', 'tasks': {}}}
        join = {'join': 'all'}
        on_success = {'on-success': ['email']}

        utils.merge_dicts(overlay['test']['tasks'], {'get': on_success})
        utils.merge_dicts(overlay['test']['tasks'], {'echo': on_success})
        utils.merge_dicts(overlay['test']['tasks'], {'email': join})

        wfs_spec = self._parse_dsl_spec(add_tasks=True,
                                        changes=overlay,
                                        expect_error=False)

        self.assertEqual(1, len(wfs_spec.get_workflows()))
        self.assertEqual('test', wfs_spec.get_workflows()[0].get_name())
        self.assertEqual('direct', wfs_spec.get_workflows()[0].get_type())
        self.assertIsInstance(wfs_spec.get_workflows()[0].get_tasks(),
                              tasks.DirectWfTaskSpecList)

    def test_direct_workflow_invalid_task(self):
        overlay = {'test': {'type': 'direct', 'tasks': {}}}
        require = {'requires': ['echo', 'get']}

        utils.merge_dicts(overlay['test']['tasks'], {'email': require})

        self._parse_dsl_spec(add_tasks=True,
                             changes=overlay,
                             expect_error=True)

    def test_reverse_workflow(self):
        overlay = {'test': {'type': 'reverse', 'tasks': {}}}
        require = {'requires': ['echo', 'get']}

        utils.merge_dicts(overlay['test']['tasks'], {'email': require})

        wfs_spec = self._parse_dsl_spec(add_tasks=True,
                                        changes=overlay,
                                        expect_error=False)

        self.assertEqual(1, len(wfs_spec.get_workflows()))
        self.assertEqual('test', wfs_spec.get_workflows()[0].get_name())
        self.assertEqual('reverse', wfs_spec.get_workflows()[0].get_type())
        self.assertIsInstance(wfs_spec.get_workflows()[0].get_tasks(),
                              tasks.ReverseWfTaskSpecList)

    def test_reverse_workflow_invalid_task(self):
        overlay = {'test': {'type': 'reverse', 'tasks': {}}}
        join = {'join': 'all'}
        on_success = {'on-success': ['email']}

        utils.merge_dicts(overlay['test']['tasks'], {'get': on_success})
        utils.merge_dicts(overlay['test']['tasks'], {'echo': on_success})
        utils.merge_dicts(overlay['test']['tasks'], {'email': join})

        self._parse_dsl_spec(add_tasks=True,
                             changes=overlay,
                             expect_error=True)

    def test_version_required(self):
        dsl_dict = copy.deepcopy(self._dsl_blank)
        dsl_dict.pop('version', None)

        exception = self.assertRaises(exc.DSLParsingException,
                                      self._spec_parser,
                                      yaml.safe_dump(dsl_dict))

        self.assertIn("'version' is a required property", exception.message)

    def test_version(self):
        tests = [
            ({'version': None}, True),
            ({'version': ''}, True),
            ({'version': '2.0'}, False),
            ({'version': 2.0}, False),
            ({'version': 2}, False)
        ]

        for version, expect_error in tests:
            self._parse_dsl_spec(add_tasks=True,
                                 changes=version,
                                 expect_error=expect_error)

    def test_inputs(self):
        tests = [
            ({'input': ['var1', 'var2']}, False),
            ({'input': ['var1', 'var1']}, True),
            ({'input': [12345]}, True),
            ({'input': [None]}, True),
            ({'input': ['']}, True),
            ({'input': None}, True),
            ({'input': []}, True),
            ({'input': ['var1', {'var2': 2}]}, False),
            ({'input': [{'var1': 1}, {'var2': 2}]}, False),
            ({'input': [{'var1': None}]}, False),
            ({'input': [{'var1': 1}, {'var1': 1}]}, True),
            ({'input': [{'var1': 1, 'var2': 2}]}, True)
        ]

        for wf_input, expect_error in tests:
            overlay = {'test': wf_input}
            self._parse_dsl_spec(add_tasks=True,
                                 changes=overlay,
                                 expect_error=expect_error)

    def test_outputs(self):
        tests = [
            ({'output': {'k1': 'a', 'k2': 1, 'k3': True, 'k4': None}}, False),
            ({'output': []}, True),
            ({'output': 'whatever'}, True),
            ({'output': None}, True),
            ({'output': {}}, True)
        ]

        for wf_output, expect_error in tests:
            overlay = {'test': wf_output}
            self._parse_dsl_spec(add_tasks=True,
                                 changes=overlay,
                                 expect_error=expect_error)

    def test_tasks_required(self):
        exception = self._parse_dsl_spec(add_tasks=False,
                                         expect_error=True)

        self.assertIn("'tasks' is a required property", exception.message)

    def test_tasks(self):
        tests = [
            ({'tasks': {}}, True),
            ({'tasks': None}, True),
            ({'tasks': self._dsl_tasks}, False)
        ]

        for wf_tasks, expect_error in tests:
            overlay = {'test': wf_tasks}
            self._parse_dsl_spec(add_tasks=False,
                                 changes=overlay,
                                 expect_error=expect_error)

    def test_task_defaults(self):
        tests = [
            ({'on-success': ['email']}, False),
            ({'on-success': [{'email': '<% 1 %>'}]}, False),
            ({'on-success': [{'email': '<% 1 %>'}, 'echo']}, False),
            ({'on-success': 'email'}, True),
            ({'on-success': None}, True),
            ({'on-success': ['']}, True),
            ({'on-success': []}, True),
            ({'on-success': ['email', 'email']}, True),
            ({'on-success': ['email', 12345]}, True),
            ({'on-error': ['email']}, False),
            ({'on-error': [{'email': '<% 1 %>'}]}, False),
            ({'on-error': [{'email': '<% 1 %>'}, 'echo']}, False),
            ({'on-error': 'email'}, True),
            ({'on-error': None}, True),
            ({'on-error': ['']}, True),
            ({'on-error': []}, True),
            ({'on-error': ['email', 'email']}, True),
            ({'on-error': ['email', 12345]}, True),
            ({'on-complete': ['email']}, False),
            ({'on-complete': [{'email': '<% 1 %>'}]}, False),
            ({'on-complete': [{'email': '<% 1 %>'}, 'echo']}, False),
            ({'on-complete': 'email'}, True),
            ({'on-complete': None}, True),
            ({'on-complete': ['']}, True),
            ({'on-complete': []}, True),
            ({'on-complete': ['email', 'email']}, True),
            ({'on-complete': ['email', 12345]}, True),
            ({'policies': {'retry': {'count': 3, 'delay': 1}}}, False),
            ({'policies': {'retry': {'count': '<% 3 %>', 'delay': 1}}},
             False),
            ({'policies': {'retry': {'count': 3, 'delay': '<% 1 %>'}}},
             False),
            ({'policies': {'retry': {'count': -3, 'delay': 1}}}, True),
            ({'policies': {'retry': {'count': 3, 'delay': -1}}}, True),
            ({'policies': {'retry': {'count': '3', 'delay': 1}}}, True),
            ({'policies': {'retry': {'count': 3, 'delay': '1'}}}, True),
            ({'policies': {'retry': None}}, True),
            ({'policies': {'wait-before': 1}}, False),
            ({'policies': {'wait-before': '<% 1 %>'}}, False),
            ({'policies': {'wait-before': -1}}, True),
            ({'policies': {'wait-before': 1.0}}, True),
            ({'policies': {'wait-before': '1'}}, True),
            ({'policies': {'wait-after': 1}}, False),
            ({'policies': {'wait-after': '<% 1 %>'}}, False),
            ({'policies': {'wait-after': -1}}, True),
            ({'policies': {'wait-after': 1.0}}, True),
            ({'policies': {'wait-after': '1'}}, True),
            ({'policies': {'timeout': 300}}, False),
            ({'policies': {'timeout': '<% 300 %>'}}, False),
            ({'policies': {'timeout': -300}}, True),
            ({'policies': {'timeout': 300.0}}, True),
            ({'policies': {'timeout': '300'}}, True),
            ({'policies': {'pause-before': False}}, False),
            ({'policies': {'pause-before': '<% False %>'}}, False),
            ({'policies': {'pause-before': 'False'}}, True),
            ({'policies': {'concurrency': 10}}, False),
            ({'policies': {'concurrency': '<% 10 %>'}}, False),
            ({'policies': {'concurrency': -10}}, True),
            ({'policies': {'concurrency': 10.0}}, True),
            ({'policies': {'concurrency': '10'}}, True)
        ]

        for default, expect_error in tests:
            overlay = {'test': {'task-defaults': {}}}
            utils.merge_dicts(overlay['test']['task-defaults'], default)
            self._parse_dsl_spec(add_tasks=True,
                                 changes=overlay,
                                 expect_error=expect_error)
