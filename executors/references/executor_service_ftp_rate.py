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

"""This scenario launches the *service_ftp_rate* scenario
from /openbach-extra/apis/scenario_builder/scenarios/
"""

from auditorium_scripts.scenario_observer import ScenarioObserver
from scenario_builder.scenarios import service_ftp_rate

def main(scenario_name='executor_service_ftp_rate', argv=None):
    observer = ScenarioObserver()
    observer.add_scenario_argument(
            '--server-entity', required=True,
            help='name of the entity for the FTP server')
    observer.add_scenario_argument(
            '--client-entity', required=True,
            help='name of the entity for the FTP client')
    observer.add_scenario_argument(
            '--server-ip', required=True, help='The server IP address')
    observer.add_scenario_argument(
            '--server-port', default = 2121,  help = 'Listened port (default = 2121)')
    observer.add_scenario_argument(
            '--mode', required = True,
            choices=['upload', 'download'], help = 'upload or download')
    observer.add_scenario_argument(
            '--user', default = 'openbach',  help = 'Authorized FTP user')
    observer.add_scenario_argument(
            '--psswrd', default = 'openbach',  help = "Authorized FTP user's password")
    observer.add_scenario_argument(
            '--multiple', type = int, default = 1, help = 'Number of transfer of the file')
    observer.add_scenario_argument(
            '--file-path', required = True, help = 'File path to transfer')
    observer.add_scenario_argument(
            '--blocksize', default = 8192, help = 'Set maximum chunk size  (default = 8192)')
    observer.add_scenario_argument(
            '--post-processing-entity', help='The entity where the post-processing will be '
            'performed (histogram/time-series jobs must be installed) if defined')

    args = observer.parse(argv, scenario_name)

    scenario = service_ftp_rate.build(
            args.server_entity,
            args.client_entity,
            args.server_ip,
            args.server_port,
            args.mode,
            args.file_path,
            args.multiple,
            args.user,
            args.psswrd,
            args.blocksize,
            args.post_processing_entity)
    observer.launch_and_wait(scenario)

if __name__ == '__main__':
    main()
