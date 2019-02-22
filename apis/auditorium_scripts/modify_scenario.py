#!/usr/bin/env python3

# OpenBACH is a generic testbed able to control/configure multiple
# network/physical entities (under test) and collect data from them. It is
# composed of an Auditorium (HMIs), a Controller, a Collector and multiple
# Agents (one for each network entity that wants to be tested).
#
#
# Copyright © 2016 CNES
#
#
# This file is part of the OpenBACH testbed.
#
#
# OpenBACH is a free software : you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.


"""Call the openbach-function modify_scenario"""


__author__ = 'Viveris Technologies'
__credits__ = '''Contributors:
 * Adrien THIBAUD <adrien.thibaud@toulouse.viveris.com>
 * Mathias ETTINGER <mathias.ettinger@toulouse.viveris.com>
'''


import json
from argparse import FileType

from frontend import FrontendBase


class ModifyScenario(FrontendBase):
    def __init__(self):
        super().__init__('OpenBACH — Modify a Scenario')
        self.parser.add_argument('name', help='name of the scenario to modify')
        self.parser.add_argument(
                'scenario', type=FileType('r'),
                help='path to the definition file of the scenario')
        self.parser.add_argument(
                '-p', '--project',
                help='name of the project the scenario is associated with')

    def parse(self, args=None):
        super().parse(args)
        scenario = self.args.scenario
        with scenario:
            try:
                self.args.scenario = json.load(scenario)
            except ValueError:
                self.parser.error('invalid JSON data in {}'.format(scenario.name))

    def execute(self, show_response_content=True):
        scenario = self.args.scenario
        name = self.args.name
        project = self.args.project
        route = 'scenario/{}/'.format(name)
        if project is not None:
            route = 'project/{}/{}'.format(project, route)

        return self.request(
                'PUT', route, **scenario,
                show_response_content=show_response_content)


if __name__ == '__main__':
    ModifyScenario.autorun()
