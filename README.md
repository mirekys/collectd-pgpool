# collectd-pgpool
[Collectd](http://www.collectd.org/) plugin for obtaining connection metrics from a running [PgPool-II](http://www.pgpool.net/mediawiki/index.php/Main_Page) instance. Based on the [collectd-python](https://collectd.org/documentation/manpages/collectd-python.5.shtml).

# Installation & Configuration

* Make sure you have configured [pcp.conf](http://www.pgpool.net/docs/latest/pgpool-en.html#config) on PgPool-II
* Clone this repo: ```git clone https://github.com/mirekys/collectd-apachelog.git```
* Place *pgpool.py* and *util.py* to your collectd-python ModulePath
* Update your collectd.conf
```
  <Plugin python>
        ModulePath "/../../collectd-plugins/"
        LogTraces false
        Interactive false
        Import ""

        Import 'pgpool'
        <Module pgpool>
                Hostname "localhost"
                PcpUser "pcpuser"
                PcpPassword "..."
                PcpPort "9898"
                PcpTimeout 1
        </Module>
</Plugin>
```

# Output

Plugin executes the following PCP command:
```
pcp_proc_info -v $PCP_TIMEOUT $PCP_HOSTNAME $PCP_PORT $PCP_USER $PCP_PASSWORD
```

Which results in following output example:
```
pgpool/count-pools=6
pgpool/count-connections_per_pool=8
pgpool/count-pools-active=6
pgpool/count-pool0-dbname-dbuser-active_connections=1
pgpool/count-pool0-dbname-dbuser-total_connections=1
pgpool/count-pool1-dbname-dbuser-active_connections=0
pgpool/count-pool1-dbname-dbuser-total_connections=3
pgpool/count-pool2-dbname-dbuser-active_connections=0
pgpool/count-pool2-dbname-dbuser-total_connections=2
pgpool/count-pool3-dbname-dbuser-active_connections=0
pgpool/count-pool3-dbname-dbuser-total_connections=2
pgpool/count-pool4-dbname-dbuser-active_connections=1
pgpool/count-pool4-dbname-dbuser-total_connections=4
pgpool/count-pool5-dbname-dbuser-active_connections=1
pgpool/count-pool5-dbname-dbuser-total_connections=4

```

# Debugging

You can run this plugin in standalone debug mode, where it outputs to console
what would be otherwise sent to the collectd daemon:

``` ./pgpool.py debug ```
