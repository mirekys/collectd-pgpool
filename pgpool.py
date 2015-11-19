#!/usr/bin/env python

""" A collectd-python plugin for obtaining
    metrics from a running PgPoolII instance. """


import sys
from util import CollectdPlugin
from subprocess import check_output


class PgPool(CollectdPlugin):
    """ Main plugin class """

    def __init__(self, debug=False):
        super(PgPool, self).__init__(debug)
        self.hostname = 'localhost'
        self.pcp_user = 'postgres'
        self.pcp_password = ''
        self.pcp_port = 9898
        self.pcp_timeout = 1
        self.pcp_args = ''
        self.pools = {}


    def configure(self, conf):
        """ Receive and process configuration block from collectd """
        for node in conf.children:
            key = node.key.lower()
            val = node.values[0]

            if key == 'hostname':
                self.hostname = val
            elif key == 'pcpuser':
                self.pcp_user = val
            elif key == 'pcppassword':
                self.pcp_password = val
            elif key == 'pcpport':
                self.pcp_port = val
            elif key == 'pcptimeout':
                self.pcp_timeout = val
            else:
                self.warn('Unknown config key: %s.' % key)

        self.plugin_name = 'pgpool-%s' % self.hostname.split('.')[0]
        self.pcp_args = "%s %s %s %s %s" % (self.pcp_timeout,
               self.hostname, self.pcp_port, self.pcp_user, self.pcp_password)


    def read_config(self, key):
        """ Obtain PgPool-II running configuration by key """
        val = check_output("pcp_pool_status %s | grep %s -A1 | tail -n1 |"\
              " awk '{print $2}'" % (self.pcp_args, key), shell=True)
        return val.strip()


    def parse_pooldata(self, pooldata):
        """ Returns connection counts and other data
            for each pool found in pooldata """
        for key in self.pools.keys():
            self.pools[key]['Connected'] = 0
            self.pools[key]['Active'] = False

        poolid = 0
        for line in pooldata.splitlines():
            key, val = [x.strip() for x in line.split(':', 1)]
            if key == 'Database':    # Process first key of a pool
                self.pools[poolid] = { 'Active' : True }

            self.pools[poolid][key] = val

            if key == 'Connected': # Process last key of a pool (considering -v)
                poolid += 1


    def read(self):
        """ Collectd read callback for getting metrics from postgres """
        pooldata = check_output('pcp_proc_info -v %s' % self.pcp_args, shell=True)
        self.parse_pooldata(pooldata)

        pool_num = self.read_config('num_init_children')
        connections_per_pool = self.read_config('max_pool')

        self.submit('count', 'pools', pool_num)
        self.submit('count', 'connections_per_pool', connections_per_pool)
        self.submit('count', 'pools-active',
            len([value for value in self.pools.values() if value['Active']]))

        for poolid, pool in self.pools.iteritems():
            # Submit currently active connections in a pool
            self.submit('count', 'pool%d-%s-%s-active_connections' %
                (poolid, pool['Database'], pool['Username']), pool['Connected'])
            # Submit total number of connections since pool creation
            self.submit('count', 'pool%d-%s-%s-total_connections' %
                (poolid, pool['Database'], pool['Username']), pool['Counter'])


if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    print('<Debugging Mode ON>')

    class NodeMock(object):
        """ Immitates single configuration item """
        def __init__(self, key, value):
            self.key = key
            self.values = [value]

    class ConfigMock(object):
        """ Immitates class passed in by collectd """
        def __init__(self, hostname, port, user, password, timeout):
            self.children = []
            self.children.append(NodeMock('hostname', hostname))
            self.children.append(NodeMock('pcpport', port))
            self.children.append(NodeMock('pcpuser', user))
            self.children.append(NodeMock('pcppassword', password))
            self.children.append(NodeMock('pcptimeout', timeout))


    from time import sleep
    sleep_time = 1
    cfg = ConfigMock('localhost', 9898,
            'your-pcp-user', 'your-pcp-password', 1)
    pgpool = PgPool(debug=True)
    pgpool.configure(cfg)
    try:
        while True:
            pgpool.read()
            sleep(sleep_time)
    except KeyboardInterrupt:
        pass
else:
    import collectd
    pgpool = PgPool()
    collectd.register_config(pgpool.configure)
    collectd.register_read(pgpool.read)
