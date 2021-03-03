#!/usr/bin/env python

# OpenBACH is a generic testbed able to control/configure multiple
# network/physical entities (under test) and collect data from them.
# It is composed of an Auditorium (HMIs), a Controller, a Collector
# and multiple Agents (one for each network entity that wants to be
# tested).
#
#
# Copyright © 2016-2020 CNES
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

"""TCP Evaluation Suite

This scenario provides a scenario that enables the evaluation of TCP
congestion controls.

The architecture should be the following

   +--------------+                                +--------------+
   | endpointA    |                                | endpointC    |
   +--------------+----+                  +--------+--------------+
                       |                  |
                     +-+-------+     +---------+
                     |Router L |     |Router R |
                     +-+-------+-----+-------+-+
                       |                     |
   +--------------+----+                     +-----+--------------+
   | endpointB    |                                | endpointD    |
   +--------------+                                +--------------+

Here are the values that should be specified by default but available for
parametrisation by the user.

+-------------------------------------+
endpointA and endpointC parameters:
  - Congestion control : CUBIC
  - IW : 10
endpointB and endpointD parameters:
  - Congestion control : CUBIC
  - IW : 10
endpointA <-> Router L,
endpointB <-> Router L,
Router R <-> endpointC,
Router R <-> endpointD,
  - bandwidth : 100 Mbps
  - latency : 10 ms
  - loss : 0%
Router L <-> Router R:
  - bandwidth : 20 Mbps
  - latency : 10 ms
  - loss : 0%
    at t=0+10s
  - bandwidth : 10 Mbps
  - latency : 10 ms
  - loss : 0%
    at t=10+10s
  - bandwidth : 20 Mbps
  - latency : 10 ms
  - loss : 0%
+-------------------------------------+

+-------------------------------------+
Traffic:
  - direction_A-C : forward or return
    (default forward)
  - direction_B-D : forward or return
    (default forward)
  - flow_size_B-D :
    - start at tBD=0
    - 500 MB
    - n_flow = 1 (can be 0)
  - flow_size_A-C :
    - start at tAC=tBD+5 sec
    - 10 MB
    - n_flow : 1
    - repeat : 10
+-------------------------------------+

+-------------------------------------+
Metrics:
  - CWND for all the flows as function of time
  - Received throughput at the receiver for all entities receiving data as a function of time
  - Time needed to transmit flow_A-C (CDF)
  - bandwidth L <-> R usage (%) as function of time
+-------------------------------------+

"""


from auditorium_scripts.scenario_observer import ScenarioObserver
from scenario_builder.scenarios import tcp_evaluation_suite

def main(argv=None):

    observer = ScenarioObserver()

    observer.add_scenario_argument(
            '--endpointA', required=True,
            help='Machine name representing endpointA')
    observer.add_scenario_argument(
            '--endpointB', required=True,
            help='Machine name representing endpointB')
    observer.add_scenario_argument(
            '--endpointC', required=True,
            help='Machine name representing endpointC')
    observer.add_scenario_argument(
            '--endpointD', required=True,
            help='Machine name representing endpointD')
    observer.add_scenario_argument(
            '--routerL', required=True,
            help='Machine name representing routerL')
    observer.add_scenario_argument(
            '--routerR', required=True,
            help='Machine name representing routerR')
    observer.add_scenario_argument(
            '--endpointC-ip', required=True,
            help='Private endpointC ip')
    observer.add_scenario_argument(
            '--endpointD-ip', required=True,
            help='Private endpointD ip')
    observer.add_scenario_argument(
            '--endpointA-network-ip', required=True,
            help='endpointA network ip with subnet mask')
    observer.add_scenario_argument(
            '--endpointB-network-ip', required=True,
            help='endpointB network ip with subnet mask')
    observer.add_scenario_argument(
            '--endpointC-network-ip', required=True,
            help='endpointC network ip with subnet mask')
    observer.add_scenario_argument(
            '--endpointD-network-ip', required=True,
            help='endpointD network ip with subnet mask')
    observer.add_scenario_argument(
            '--routerL-to-endpointA-ip', required=True,
            help='routerL to endpointA interface ip')
    observer.add_scenario_argument(
            '--routerL-to-endpointB-ip', required=True,
            help='routerL to endpointB interface ip')
    observer.add_scenario_argument(
            '--routerR-to-endpointC-ip', required=True,
            help='routerR to endpointC interface ip')
    observer.add_scenario_argument(
            '--routerR-to-endpointD-ip', required=True,
            help='routerR to endpointD interface ip')
    observer.add_scenario_argument(
            '--routerL-to-routerR-ip', required=True,
            help='routerL to routerR interface ip')
    observer.add_scenario_argument(
            '--routerR-to-routerL-ip', required=True,
            help='routerR to routerL interface ip')
    observer.add_scenario_argument(
            '--interface-AL', required=True,
            help='Interface name from endpointA to routerL')
    observer.add_scenario_argument(
            '--interface-BL', required=True,
            help='Interface name from endpointB to routerL')
    observer.add_scenario_argument(
            '--interface-CR', required=True,
            help='Interface name from endpointC to routerR')
    observer.add_scenario_argument(
            '--interface-DR', required=True,
            help='Interface name from endpointD to routerR')
    observer.add_scenario_argument(
            '--interface-RA', required=True,
            help='Interface name from routerR to endpointA')
    observer.add_scenario_argument(
            '--interface-RB', required=True,
            help='Interface name from routerR to endpointB')
    observer.add_scenario_argument(
            '--interface-LC', required=True,
            help='Interface name from routerL to endpointC')
    observer.add_scenario_argument(
            '--interface-LD', required=True,
            help='Interface name from routerL to endpointD')
    observer.add_scenario_argument(
            '--interface-LA', required=True,
            help='Interface name from routerL to endpointA')
    observer.add_scenario_argument(
            '--interface-LB', required=True,
            help='Interface name from routerL to endpointB')
    observer.add_scenario_argument(
            '--interface-RC', required=True,
            help='Interface name from routerR to endpointC')
    observer.add_scenario_argument(
            '--interface-RD', required=True,
            help='Interface name from routerR to endpointD')
    observer.add_scenario_argument(
            '--interface-LR', required=True,
            help='Interface name from routerL to routerR')
    observer.add_scenario_argument(
            '--interface-RL', required=True,
            help='Interface name from routerR to routerL')

    observer.add_scenario_argument(
            '--congestion-control', required=True,
            help='Congestion control name. Ex: CUBIC')

    observer.add_scenario_argument(
            '--server-port', required=False, default=7001,
            help='Destination port for the iperf3 traffic')

    observer.add_scenario_argument(
            '--BD-file-size', required=False, default='500M',
            help='size of the file to transmit (in bytes) for B -> D transfer. '
            'The value must be stricly higher than 1 MB')
    observer.add_scenario_argument(
            '--AC-file-size', required=False, default='10M',
            help='size of the file to transmit (in bytes) for A -> C transfer. '
            'The value must be stricly higher than 1 MB')

    observer.add_scenario_argument(
            '--delay', required=False, nargs='*', type=int, default=[10,10,10],
            help='delay/latency for network_configure_link job')
    observer.add_scenario_argument(
            '--loss', required=False, nargs='*', type=int, default=[0,0,0],
            help='parameters of the loss model for tc_configure_link job')
    observer.add_scenario_argument(
            '--bandwidth', required=False, nargs='*', type=str, default=['20M','10M','20M'],
            help='bandwidth for tc_configure_link job')

    observer.add_scenario_argument(
            '--post-processing-entity', help='The entity where the post-processing will be performed '
            '(histogram/time-series jobs must be installed) if defined')


    args = observer.parse(argv, tcp_evaluation_suite.SCENARIO_NAME)

    scenario = tcp_evaluation_suite.build(
            args.endpointA,
            args.endpointB,
            args.endpointC,
            args.endpointD,
            args.routerL,
            args.routerR,
            args.endpointC_ip,
            args.endpointD_ip,
            args.server_port,
            args.endpointA_network_ip,
            args.endpointB_network_ip,
            args.endpointC_network_ip,
            args.endpointD_network_ip,
            args.routerL_to_endpointA_ip,
            args.routerL_to_endpointB_ip,
            args.routerR_to_endpointC_ip,
            args.routerR_to_endpointD_ip,
            args.routerL_to_routerR_ip,
            args.routerR_to_routerL_ip,
            args.interface_AL,
            args.interface_BL,
            args.interface_CR,
            args.interface_DR,
            args.interface_RA,
            args.interface_RB,
            args.interface_LC,
            args.interface_LD,
            args.interface_LA,
            args.interface_LB,
            args.interface_RC,
            args.interface_RD,
            args.interface_LR,
            args.interface_RL,
            args.BD_file_size,
            args.AC_file_size,
            args.delay,
            args.loss,
            args.bandwidth,
            congestion_control=args.congestion_control,
            post_processing_entity=args.post_processing_entity,
            scenario_name=args.scenario_name)

    observer.launch_and_wait(scenario)

if __name__ == '__main__':
    main()
