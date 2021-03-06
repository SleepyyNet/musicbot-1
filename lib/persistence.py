# -*- coding: utf-8 -*-
import click
import aioredis
import os
from logging import debug

DEFAULT_REDIS_ADDRESS = 'redis://localhost'
DEFAULT_REDIS_DB = 0
DEFAULT_REDIS_PASSWORD = None

options = [
    click.option('--redis-address', envvar='MB_REDIS_ADDRESS', help='Redis URI', default=DEFAULT_REDIS_ADDRESS),
    click.option('--redis-db', envvar='MB_REDIS_DB', help='Redis index DB', default=DEFAULT_REDIS_DB),
    click.option('--redis-password', envvar='MB_REDIS_PASSWORD', help='Redis password', default=DEFAULT_REDIS_PASSWORD),
]


class Persistence(object):
    def __init__(self, redis_address=None, redis_database=None, redis_password=None, **kwargs):
        self.address = redis_address if redis_address is not None else os.getenv('MB_REDIS_ADDRESS', DEFAULT_REDIS_ADDRESS)
        self.database = redis_database if redis_database is not None else os.getenv('MB_REDIS_DB', DEFAULT_REDIS_DB)
        self.password = redis_password if redis_password is not None else os.getenv('MB_REDIS_PASSWORD', DEFAULT_REDIS_PASSWORD)
        debug('REDIS: {} {} {}'.format(self.address, self.database, self.password))

    async def connect(self):
        self.conn = await aioredis.create_connection(self.address, db=self.database, password=self.password)

    async def execute(self, command, *args, **kwargs):
        return await self.conn.execute(command, *args, **kwargs)

    async def close(self):
        self.conn.close()
        await self.conn.wait_closed()
