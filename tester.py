# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from base import Tester
from exabgp import ExaBGP
import os
from  settings import dckr

def rm_line():
    pass
    #print '\x1b[1A\x1b[2K\x1b[1D\x1b[1A'


class ExaBGPTester(Tester, ExaBGP):

    CONTAINER_NAME_PREFIX = 'bgperf_exabgp_tester_'

    def __init__(self, name, host_dir, conf, image='bgperf/exabgp'):
        super(ExaBGPTester, self).__init__(name, host_dir, conf, image)

    def configure_neighbors(self, target_conf):
        peers = self.conf.get('neighbors', {}).values()

        for p in peers:
            with open('{0}/{1}.conf'.format(self.host_dir, p['router-id']), 'w+') as f:
                local_address = p['local-address']
                config = '''neighbor {0} {{
    peer-as {1};
    router-id {2};
    local-address {3};
    local-as {4};
    static {{
'''.format(target_conf['local-address'], target_conf['as'],
               p['router-id'], local_address, 1000)
                f.write(config)
                for path in p['paths']:
                    f.write('      route {0} next-hop {1} as-path [ 100 ];\n'.format(path, local_address))
                f.write('''   }
}
''')
                for p1 in peers:
                    if p != p1:
                        local_address = p['local-address']
                        config = '''neighbor {0} {{
    peer-as {1};
    router-id {2};
    local-address {3};
    local-as {4};
    static {{
'''.format(p1['local-address'], target_conf['as'],
               p['router-id'], local_address, 1000)
                        f.write(config)
                        for path in p['paths']:
                            f.write('      route {0} next-hop {1} as-path [ 100 ];\n'.format(path, local_address))
                        f.write('''   }
}
''')

    def get_startup_cmd(self):
        startup = ['''#!/bin/bash
ulimit -n 65536
mkdir -p /usr/local/bin/etc/exabgp/
mkdir -p /run/exabgp/
mkdir -p /root/config/run/
mkfifo /run/exabgp.{in,out}
exabgp env > /usr/local/bin/etc/exabgp/exabgp.env''']

        peers = self.conf.get('neighbors', {}).values()
        for p in peers:
            startup.append('''env exabgp.tcp.bind={2} exabgp.tcp.port=179 exabgp.log.destination={0}/{1}.log \
exabgp.daemon.daemonize=true \
exabgp.daemon.user=root \
exabgp {0}/{1}.conf'''.format(self.guest_dir, p['router-id'], p['router-id']))
        return '\n'.join(startup)
