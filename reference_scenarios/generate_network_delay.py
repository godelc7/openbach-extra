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

"""This script launches the *network_delay* scenario
from /openbach-extra/apis/scenario_builder/scenarios/
"""

from auditorium_scripts.scenario_observer import ScenarioObserver
from scenario_builder.scenarios import network_delay


def main(scenario_name='generate_network_delay', argv=None):
    observer = ScenarioObserver()
    observer.add_scenario_argument(
            '--clt_entity', '--clt', required=True,
            help='name of the entity for the client of the RTT tests')
    observer.add_scenario_argument(
            '--srv_entity', '--srv', required=True,
            help='name of the entity for the srv of the RTT tests')
    observer.add_scenario_argument(
            '--clt_ip', required=True, help='IP address of source of pings and packets')
    observer.add_scenario_argument(
            '--srv_ip', required=True, help='destination ip address and target of the pings')
    observer.add_scenario_argument(
            '--duration', default=10, help='duration of delay scenario (s)')
    observer.add_scenario_argument(
            '--simultaneous', action='store_true',
            help='option whether or not the test is simultaneous. Default sequential')
    observer.add_scenario_argument(
            '--entity_pp', help='The entity where the post-processing will be '
            'performed (histogram/time-series jobs must be installed) if defined')

    args = observer.parse(argv, scenario_name)

    scenario = network_delay.build(
                      args.clt_entity,
                      args.srv_entity,
                      args.clt_ip,
                      args.srv_ip,
                      args.duration,
                      args.simultaneous,
                      args.entity_pp)
    observer.launch_and_wait(scenario)


if __name__ == '__main__':
    main()
