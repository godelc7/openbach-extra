#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# OpenBACH is a generic testbed able to control/configure multiple
# network/physical entities (under test) and collect data from them.
# It is composed of an Auditorium (HMIs), a Controller, a Collector
# and multiple Agents (one for each network entity that wants to be
# tested).
#
#
# Copyright © 2016-2019 CNES
#
#
# This file is part of the OpenBACH testbed.
#
#
# OpenBACH is a free software : you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

"""This scenario builds and launches the *network_qos* scenario
from /openbach-extra/apis/scenario_builder/scenarios/
"""


from auditorium_scripts.scenario_observer import ScenarioObserver
from scenario_builder.scenarios import network_qos


def main(scenario_name='network_qos', argv=None):
    observer = ScenarioObserver()
    observer.add_scenario_argument(
            '--entity', '--entity', required=True,
            help='Name of the entity to place the scheduler')
    observer.add_scenario_argument(
            '--interface', '--network_interface', required=True,
            help='The interface on the entity to place the scheduler')
    observer.add_scenario_argument(
            '--action', choices=['add', 'remove'], required=True,
            help='Add a new scheduler or remove the existing one')
    observer.add_scenario_argument(
            '--path',
            help='The path to the scheduler configuartion file, on the entity, mandatory if action is add')
    
    args = observer.parse(argv, scenario_name)

    if args.action == "add":
        if not args.path:
            raise AttributeError("Path must be specified if the action is add")

    scenario = network_qos.build(
                args.entity,
                args.interface,
                args.action,
                args.path,
    )
    observer.launch_and_wait(scenario)


if __name__ == '__main__':
    main()