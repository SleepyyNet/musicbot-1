from logging import debug, info
from .helpers import drier, timeit
from . import filter
import asyncpg
import sys
import os


class DbContext(object):
    settings = {
        'host': 'localhost',
        'port': 5432,
        'database': 'musicbot',
        'user': 'postgres',
        'password': 'musicbot', }
    schema = 'public'
    insert_log = '''insert into musics_log (artist, album, genre, folder, youtube, number, rating, duration, size, title, path, keywords) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)'''

    def __init__(self, **kwargs):
        for s in self.settings.keys():
            if s in kwargs:
                self.settings[s] = kwargs[s]
        print(self.settings)
        self._pool = None
        info(self.connection_string())

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.settings['user'], self.settings['password'], self.settings['host'], self.settings['port'], self.settings['database'])

    @drier
    @timeit
    async def upsert(self, m):
        sql = '''select * from upsert($1::music)'''
        l = m.to_list()
        print(l)
        await self.execute(sql, l)

    async def filter(self, f=filter.Filter()):
        sql = '''select * from do_filter($1::filter)'''
        l = f.to_list()
        print(l)
        return await self.fetch(sql, l)

    # @drier
    # @timeit
    # async def upsertall(self, musics):
    #     sql = '''select * from upsert_all($1::music[])'''
    #     # await self.execute(sql, [[m.title, m.album, m.genre, m.artist, m.folder, m.youtube, m.number, m.path, m.rating, m.duration, m.size, m.keywords] for m in musics])
    #     await self.execute(sql, musics)
    #     # async with (await self.pool).acquire() as connection:
    #     #     stmt = await connection.prepare(sql)
    #     #     print(stmt.get_parameters())
    #     #     await stmt.fetch(musics)

    @drier
    @timeit
    async def append(self, m):
        await self.execute(self.insert_log, m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords)

    @drier
    @timeit
    async def appendall(self, musics):
        for m in musics:
            await self.execute(self.insert_log, m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords)

    @drier
    @timeit
    async def appendmany(self, musics):
        async with (await self.pool).acquire() as connection:
            await connection.executemany(self.insert_log, musics)
        # await self.executemany(sql, musics)

    def __str__(self):
        return self.connection_string()

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
        return self._pool

    @timeit
    async def fetch(self, *args, **kwargs):
        info('fetching: {}'.format(*args))
        return (await (await self.pool).fetch(*args, **kwargs))

    @drier
    @timeit
    async def executefile(self, filepath):
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        info('loading schema: {}'.format(schema_path))
        with open(schema_path, "r") as s:
            sql = s.read()
            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await connection.execute(sql)

    @drier
    @timeit
    async def execute(self, sql, *args, **kwargs):
        debug(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.execute(sql, *args, **kwargs)

    @drier
    @timeit
    async def executemany(self, sql, *args, **kwargs):
        debug(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.executemany(sql, *args, **kwargs)

    async def create(self):
        debug('db create')
        sql = 'create schema if not exists {}'.format(self.schema)
        await self.execute(sql)
        await self.executefile('lib/musicbot.sql')

    async def drop(self):
        debug('db drop')
        sql = 'drop schema if exists {} cascade'.format(self.schema)
        await self.execute(sql)

    async def clear(self):
        debug('clear')
        await self.drop()
        await self.create()

    async def folders(self):
        sql = '''select name from folders'''
        return await self.fetch(sql)
