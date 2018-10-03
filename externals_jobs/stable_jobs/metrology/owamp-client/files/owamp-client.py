#!/usr/bin/env python3
#  OpenBACH is a generic testbed able to control/configure multiple
#  network/physical entities (under test) and collect data from them. It is
#  composed of an Auditorium (HMIs), a Controller, a Collector and multiple
#  Agents (one for each network entity that wants to be tested).
#
#
#  Copyright © 2018 CNES
#
#
#  This file is part of the OpenBACH testbed.
#
#
#  OpenBACH is a free software : you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
#  more details. # # You should have received a copy of the GNU General Public License along with
#  this program. If not, see http://www.gnu.org/licenses/.


"""Sources of the Job owamp-client"""


__author__ = 'Silicom'
__credits__ = '''Contributor: Marlene MOST <mmost@silicom.fr>'''


import syslog
import argparse
import subprocess
import numpy as np
from sys import exit
from time import sleep

import collect_agent


def build_parser():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('destination_address', type=str, help='Address of destination')
    parser.add_argument('-c', type=int, dest='count', default=100, help='number of test packets to send '
                                                                        'Default = 100 packets')

    parser.add_argument('-i', type=str, dest='interval',
                        help='mean average time between packets (seconds)'
                             'e=exponential distribution of the packets'
                             'f=constant distribution of the packets'
                             'Default = 0.1e')

    return parser


def timestamp(data):
    # Convert timestamp obtained from owping output
    # into readable time (in ms) for send_stat function
    return int((float(data) * 1000))


def client(destination_address, count, interval):

    # the length of the sample used to compute jitter mean
    granularity = 5

    conffile = "/opt/openbach/agent/jobs/owamp-client/owamp-client_rstats_filter.conf"

    # case of output == raw data (singleton metric)
    cmd = ['owping', '-U', '-v', destination_address]

    if count:
        cmd += ['-c', str(count)]

    if interval:
        cmd += ['-i', interval]

    success = collect_agent.register_collect(conffile)
    if not success:
        message = 'ERROR connecting to rstats'
        collect_agent.send_log(syslog.LOG_ERR, message)
        exit(message)

    collect_agent.send_log(syslog.LOG_DEBUG, 'Starting job opwing')

    # launch command
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # if something wrong happens
    error_log = p.stderr.readline()
    if error_log:
        collect_agent.send_log(syslog.LOG_ERR, 'Errror when launching owping: {}'.format(error_log))
        exit(1)

    # read the first lines and do nothing with (useless --> no information)
    useless_data = p.stdout.readline().decode()
    while not useless_data.startswith('SID:'):
        useless_data = p.stdout.readline().decode()

    # delay tab
    delay_tab = []

    # jitter tab
    ipdv_tab = []
    time_tab = []

    n = 0
    # get data from up link
    while n < count:

        n += 1

        # read output containing delay value
        output_sent = p.stdout.readline().decode()

        if not output_sent:
            if p.poll is not None:
                break
                continue

        # packet lost
        if 'LOST' in output_sent.split()[1]:
            message = 'Warning: Packet lost.'
            collect_agent.send_log(syslog.LOG_ERR, message)
            continue

        # src and dst are not sync
        if 'unsync' in output_sent.split()[3]:
            message = 'Error: No synchronization between client and server. Results not available.'
            collect_agent.send_log(syslog.LOG_ERR, message)
            exit(message)

        # extract delay value in ms
        delay_sent = float(output_sent.split()[1].split("=")[1])

        # get current timestamp corresponding to delay value of interest
        sent_timestamp = output_sent.split()[7].split("=")[1]  # raw data

        collect_agent.send_stat(timestamp(sent_timestamp),
                                owd_sent=delay_sent)

        delay_tab.append(delay_sent)

        # compute inter-packet delay variation (in ms)
        if n > 1:
            ipdv_sent = abs(delay_sent - delay_sent_old)
            ipdv_tab.append(ipdv_sent)
            time_tab.append(timestamp(sent_timestamp))

            if n % granularity == 0:
                statistics = {'inter-packet delay variation sent (ms)': np.mean(ipdv_tab)}
                collect_agent.send_stat(timestamp(sent_timestamp), **statistics)

                # clear ipdv_tab and time_tab
                ipdv_tab.clear()
                time_tab.clear()

                # compute packet delay variation (95th percentile - 50th percentile)
                pdv = np.percentile(delay_tab, 95) - np.percentile(delay_tab, 50)
                statistics = {'packet delay variation P95-P50 sent (ms)': pdv}
                collect_agent.send_stat(timestamp(sent_timestamp), **statistics)

                # clear delay_tab
                delay_tab.clear()

        delay_sent_old = delay_sent

    delay_tab.clear()
    ipdv_tab.clear()
    time_tab.clear()

    # get data from return link and throw away the 14 following lines
    # (overhead between up and return data)
    inter_data = p.stdout.readline().decode()
    while not inter_data.startswith('SID:'):
        inter_data = p.stdout.readline().decode()

    # first SID shows results from sent one-way delay
    # there is a second SID from received one-way delay
    inter_data = p.stdout.readline().decode()
    while not inter_data.startswith('SID:'):
        inter_data = p.stdout.readline().decode()

    m = 0
    while m < count:

        m += 1

        # read output
        output_received = p.stdout.readline().decode()

        if not output_received:
            if p.poll is not None:
                break
                continue

        # packet lost
        if 'LOST' in output_received.split()[1]:
            message = 'Warning: Packet lost.'
            collect_agent.send_log(syslog.LOG_ERR, message)
            continue

        # extract delay value in ms
        delay_received = float(output_received.split()[1].split("=")[1])

        # get current timestamp corresponding to delay value of interest
        received_timestamp = output_received.split()[7].split("=")[1]  # raw data

        # send received delay stats
        collect_agent.send_stat(timestamp(received_timestamp),
                                owd_received=delay_received)

        delay_tab.append(delay_received)

        # compute inter-packet delay variation (in ms)
        if m > 1:
            ipdv_received = abs(delay_received - delay_received_old)
            ipdv_tab.append(ipdv_received)
            time_tab.append(timestamp(received_timestamp))

            if m % granularity == 0:
                statistics = {'inter-packet delay variation received (ms)': np.mean(ipdv_tab)}
                collect_agent.send_stat(timestamp(received_timestamp), **statistics)

                # clear ipdv_tab and time_tab
                ipdv_tab.clear()
                time_tab.clear()

                # compute packet delay variation (95th percentile - 50th percentile)
                pdv = np.percentile(delay_tab, 95) - np.percentile(delay_tab, 50)
                statistics = {'packet delay variation P95-P50 received (ms)': pdv}
                collect_agent.send_stat(timestamp(received_timestamp), **statistics)

                # clear delay_tab
                delay_tab.clear()

        delay_received_old = delay_received

    ipdv_tab.clear()
    time_tab.clear()
    delay_tab.clear()


if __name__ == '__main__':
    args = build_parser().parse_args()
    client(args.destination_address, args.count, args.interval)





