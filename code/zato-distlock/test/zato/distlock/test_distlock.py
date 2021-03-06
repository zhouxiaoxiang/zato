# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# gevent
from gevent import sleep

# Zato
from zato.common.test import rand_int, rand_string
from zato.distlock import DEFAULT, LockManager, LockTimeout, LOCK_TYPE

# ################################################################################################################################

class _Base(TestCase):
    """ Base class for all distributed lock-related tests implementing common test cases.
    """
    backend_type = None
    is_set_up = False

# ################################################################################################################################

    def test_lock_info_name_no_namespace(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()
        lock_manager = LockManager(self.backend_type, default_ns)

        with lock_manager(name) as lock_info:
            self.assertEquals(lock_info.namespace, default_ns)
            self.assertEquals(lock_info.name, name)
            self.assertEquals(lock_info.ttl, DEFAULT.TTL)
            self.assertEquals(lock_info.acquired, True)
            self.assertEquals(lock_info.lock_type, LOCK_TYPE.PERMANENT)
            self.assertEquals(lock_info.block, DEFAULT.BLOCK)
            self.assertEquals(lock_info.block_interval, DEFAULT.BLOCK_INTERVAL)

# ################################################################################################################################

    def test_lock_info_name_with_namespace(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()
        ns = rand_string(7)
        lock_manager = LockManager(self.backend_type, default_ns)

        with lock_manager(name, ns) as lock_info:
            self.assertEquals(lock_info.namespace, ns)
            self.assertEquals(lock_info.name, name)
            self.assertEquals(lock_info.ttl, DEFAULT.TTL)
            self.assertEquals(lock_info.acquired, True)
            self.assertEquals(lock_info.lock_type, LOCK_TYPE.PERMANENT)
            self.assertEquals(lock_info.block, DEFAULT.BLOCK)
            self.assertEquals(lock_info.block_interval, DEFAULT.BLOCK_INTERVAL)

# ################################################################################################################################

    def test_lock_info_name_with_attrs(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()
        ns = rand_string(7)
        ttl = rand_int()
        block = rand_int()
        block_interval = rand_int()
        lock_manager = LockManager(self.backend_type, default_ns)

        with lock_manager(name, ns, ttl, block, block_interval) as lock_info:
            self.assertEquals(lock_info.namespace, ns)
            self.assertEquals(lock_info.name, name)
            self.assertEquals(lock_info.ttl, ttl)
            self.assertEquals(lock_info.acquired, True)
            self.assertEquals(lock_info.lock_type, LOCK_TYPE.PERMANENT)
            self.assertEquals(lock_info.block, block)
            self.assertEquals(lock_info.block_interval, block_interval)

# ################################################################################################################################

    def test_acquire_already_taken_auto_release(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()

        lock_manager = LockManager(self.backend_type, default_ns)

        lock1 = lock_manager.acquire(name, ttl=1)
        self.assertEquals(lock1.acquired, True)

        # This will not obtain the lock because it's just been taken above ..
        lock2 = lock_manager.acquire(name, block=False)
        self.assertEquals(lock2.acquired, False)

        # .. however, if we wait a moment we will get it because the original will have expired.
        sleep(2)
        lock3 = lock_manager.acquire(name)
        self.assertEquals(lock3.acquired, True)

# ################################################################################################################################

    def test_acquire_already_taken_manual_release(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()

        lock_manager = LockManager(self.backend_type, default_ns)

        lock1 = lock_manager.acquire(name, ttl=10)
        self.assertEquals(lock1.acquired, True)

        # This will not obtain the lock because it's just been taken above ..
        lock2 = lock_manager.acquire(name, block=False)
        self.assertEquals(lock2.acquired, False)

        # .. however, if we release the lock manually it will become available straightaway.
        lock1.release()

        lock3 = lock_manager.acquire(name)
        self.assertEquals(lock3.acquired, True)

# ################################################################################################################################

    def test_acquire_already_taken_lock_timeout(self):

        if not self.is_set_up:
            return

        name = rand_string()
        default_ns = rand_string()

        lock_manager = LockManager(self.backend_type, default_ns)

        lock1 = lock_manager.acquire(name, ttl=2)
        self.assertEquals(lock1.acquired, True)

        # This raises LockTimeout because we wait for 1 second only and the lock above has ttl of 2 seconds.
        try:
            lock_manager.acquire(name, block=1)
        except LockTimeout, e:
            expected = 'Could not obtain lock for `{}` `{}` within 1s'.format(default_ns, name)
            self.assertEquals(e.args[0], expected)
        else:
            self.fail('Expected a LockTimeout here')

# ################################################################################################################################

class FCNTLLockTestCase(_Base):
    backend_type = 'fcntl'

    def setUp(self):
        self.is_set_up = True

# ################################################################################################################################

class MySQLLockTestCase(_Base):
    backend_type = 'mysql+pymysql'

    def setUp(self):
        self.is_set_up = False

# ################################################################################################################################

class PostgresSQLLockTestCase(_Base):
    backend_type = 'postgresql+pg8000'

    def setUp(self):
        self.is_set_up = False

# ################################################################################################################################
