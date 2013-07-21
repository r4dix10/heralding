# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

import unittest

from mock import Mock
import gevent

from beeswarm.feeder.consumer.loggers.loggerbase import LoggerBase
from beeswarm.feeder.models.session import BeeSession
from beeswarm.feeder.consumer.consumer import Consumer


class Consumer_test(unittest.TestCase):
    def test_logging_done_bee(self):
        """
        Tests that the consumer calls a logger class and that the beesession is removed
        from the queue afterwards.
        """
        sessions = {}
        BeeSession.feeder_id = 'dummy_feeder_id'
        BeeSession.hive_id = 'dummy_hive_id'

        beesession = BeeSession('telnet', 'james', 'bond', 'foo', '1234', '4321')
        beesession.alldone = True
        sessions[beesession.id] = beesession

        #mock a dummy logger
        dummy_logger = LoggerBase({})
        log_mock = Mock()
        dummy_logger.log = log_mock

        consumer = Consumer(sessions, {})
        #inject the dummy logger into the consumer
        consumer.active_loggers = [dummy_logger]
        gevent.spawn(consumer.start_handling)
        #forcing cooperative yield.
        gevent.sleep(0)

        #assert that the log method of the logger object was called with beesession as parameter.
        dummy_logger.log.assert_called_once_with(beesession)
        #assert that the beesession was removed from the queue
        self.assertEquals(len(sessions), 0)
        consumer.stop_handling()

    def test_logging_not_done_bee(self):
        """
        Tests that the consumer does not process honeybees that are not marked as done.
        """
        sessions = {}
        BeeSession.feeder_id = 'dummy_feeder_id'
        BeeSession.hive_id = 'dummy_hive_id'

        beesession = BeeSession('telnet', 'james', 'bond', 'foo', '1234', '4321')
        beesession.alldone = False
        sessions[beesession.id] = beesession

        #mock a dummy logger
        dummy_logger = LoggerBase({})
        log_mock = Mock()
        dummy_logger.log = log_mock

        consumer = Consumer(sessions, {})
        #inject the dummy logger into the consumer
        consumer.active_loggers = [dummy_logger]
        gevent.spawn(consumer.start_handling)
        #forcing cooperative yield.
        gevent.sleep(0)

        #assert that the log method was not called
        self.assertFalse(log_mock.called)
        #assert that we still has a single item in the queue
        self.assertEquals(len(sessions), 1)
        consumer.stop_handling()


