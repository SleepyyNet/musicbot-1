# -*- coding: utf-8 -*-
import click
from lib import filter, helpers, collection


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx, **kwargs):
    '''Inconsistencies management'''


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(filter.options)
async def errors(ctx, **kwargs):
    '''Detect errors'''
    ctx.obj.db = collection.collection(**kwargs)
    mf = filter.Filter(**kwargs)
    errors = await ctx.obj.db.errors(mf)
    for e in errors:
        print(e)
