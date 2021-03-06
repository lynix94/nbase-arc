#
# Copyright 2015 Naver Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest
import testbase
import util
import gateway_mgmt
import redis_mgmt
import load_generator
import config
import time
import default_cluster
import config


class TestConsistentRead( unittest.TestCase ):
    cluster = config.clusters[0]
    max_load_generator = 10
    load_gen_thrd_list = {}

    @classmethod
    def setUpClass( cls ):
        cls.conf_checker = default_cluster.initialize_starting_up_smr_before_redis( cls.cluster )
        assert cls.conf_checker != None, 'failed to initialize cluster'

        slave = util.get_server_by_role( cls.cluster['servers'], 'slave' )

        for i in range( cls.max_load_generator ):
            cls.load_gen_thrd_list[i] = load_generator.LoadGenerator( i, slave['ip'], slave['redis_port'] )
            cls.load_gen_thrd_list[i].start()

    @classmethod
    def tearDownClass( cls ):
        for i in range( len( cls.load_gen_thrd_list ) ):
            cls.load_gen_thrd_list[i].quit()
        for i in range( len( cls.load_gen_thrd_list ) ):
            cls.load_gen_thrd_list[i].join()

        testbase.defaultTearDown(cls)

    def setUp( self ):
        util.set_process_logfile_prefix( 'TestConsistentRead_%s' % self._testMethodName )
        return 0

    def tearDown( self ):
        return 0

    def test_1_consistent_while_slave_is_in_load( self ):
        util.print_frame()
        ip, port = util.get_rand_gateway( self.cluster )
        gw = gateway_mgmt.Gateway( ip )
        gw.connect( ip, port )

        max_key = 5
        key_base = 'load_gen_key'
        for idx in range( max_key ):
            cmd = 'set %s%d 0\r\n' % (key_base, idx)
            gw.write( cmd )
            gw.read_until( '\r\n', 10 )

        try_count = 9999
        for value in range( try_count ):
            for idx in range( max_key ):
                cmd = 'set %s%d %d\r\n' % (key_base, idx, value)
                gw.write( cmd )
                response = gw.read_until( '\r\n', 10 )
                self.assertEquals( response, '+OK\r\n' )

                cmd = 'get %s%d\r\n' % (key_base, idx)
                gw.write( cmd )
                response = gw.read_until( '\r\n', 10 )
                response = gw.read_until( '\r\n', 10 )

                self.assertEquals( response, '%s\r\n' % (value), 'fail! original_value:%d, return_from_slave:%s' % (value, response[1:]) )
