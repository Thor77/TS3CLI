from datetime import timedelta

import click

from ts3py import TS3Query

from .utils import (cid_option, clid_option, count_to_str, msg_option,
                    sid_option)


@click.group()
@click.option('--host', help='teamspeak query host', default='localhost')
@click.option(
    '--port', type=int, help='teamspeak query port', default=10011,
)
@click.option('--username', help='query username', required=True)
@click.option('--password', help='query password', required=True)
@click.pass_context
def ts3cli(ctx, host, port, username, password):
    query = TS3Query(host, port)
    query.login(username, password)
    ctx.obj = {}
    ctx.obj['query'] = query


@ts3cli.resultcallback()
@click.pass_context
def disconnect(ctx, result, **kwargs):
    # disconnect from query
    ctx.obj['query'].command('quit')


@ts3cli.command()
@click.pass_context
def server(ctx):
    '''
    List virtual servers
    '''
    click.echo(', '.join(map(
        lambda vs: '{virtualserver_name} ({virtualserver_id}) - '
        '{clientsonline}'.format(
            clientsonline=count_to_str(
                vs['virtualserver_clientsonline'], 'client'
            ) + ' online',
            **vs
        ),
        ctx.obj['query'].command('serverlist')
    )))


@ts3cli.command()
@msg_option
@click.pass_context
def gm(ctx, msg):
    '''
    Send a global message
    '''
    ctx.obj['query'].command('gm', params={'msg': msg})


@ts3cli.command()
@sid_option
@click.pass_context
def clients(ctx, sid):
    '''
    List clients on a virtual server
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    click.echo(', '.join(map(
        lambda client: '{client_nickname} ({clid})'.format(**client),
        filter(
            lambda c: c['client_type'] == 0,
            ctx.obj['query'].command('clientlist')
        )
    )))


@ts3cli.command()
@sid_option
@clid_option
@click.pass_context
def clientinfo(ctx, sid, clid):
    '''
    View detailed information about a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    client_info = ctx.obj['query'].command(
        'clientinfo', params={'clid': clid})[0]
    click.echo(
        '''Nickname: {client_nickname}
Description: {client_description}
ID: {clid}
Database ID: {client_database_id}
Unique Identifier: {client_unique_identifier}
Version/Platform: {client_version} on {client_platform}
IP: {connection_client_ip}
Country: {client_country}
Connection time: {connection_time}'''.format(
            **client_info, clid=clid, connection_time=timedelta(
                milliseconds=client_info['connection_connected_time'])
        )
    )


@ts3cli.command()
@sid_option
@click.pass_context
def channel(ctx, sid):
    '''
    List channel on a virtual server
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    click.echo(', '.join(map(
        lambda channel: '{channel_name} ({cid}){clients}'.format(
            **channel,
            clients=' - {}'.format(
                count_to_str(channel['total_clients'], 'client')
            ) if channel['total_clients'] >= 1 else ''
        ),
        ctx.obj['query'].command('channellist')
    )))


@ts3cli.command()
@sid_option
@cid_option
@click.pass_context
def channelinfo(ctx, sid, cid):
    '''
    View detailed information about a channel
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    channel_info = ctx.obj['query'].command(
        'channelinfo', params={'cid': cid})[0]
    click.echo(
        '''Name: {channel_name}
Topic: {channel_topic}
Description: {channel_description}
Password: {password}
Type: {type}
Max clients: {maxclients}
Filepath: {channel_filepath}
Icon: {channel_icon_id}
'''.format(
            **channel_info,
            password='yes' if channel_info['channel_password'] else 'no',
            maxclients=(
                '∞' if channel_info['channel_maxclients'] == -1
                else channel_info['channel_maxclients']
            ),
            type=list(filter(lambda t: t[1], [
                ('permanent', channel_info['channel_flag_permanent']),
                (
                    'semi_permanent',
                    channel_info['channel_flag_semi_permanent']
                ),
                ('temporary', 1)
            ]))[0][0]
        )
    )


@ts3cli.command()
@sid_option
@clid_option
@msg_option
@click.pass_context
def poke(ctx, sid, clid, msg):
    '''
    Poke a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    ctx.obj['query'].command('clientpoke', params={'clid': clid, 'msg': msg})


@ts3cli.command()
@sid_option
@clid_option
@click.option('--reason', help='kick reason')
@click.option(
    '--channel', help='kick from channel', is_flag=True, default=False
)
@click.pass_context
def kick(ctx, sid, clid, reason, channel):
    '''
    Kick a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    params = {
        'clid': clid,
        'reasonid': 4 if channel else 5
    }
    if reason:
        params['reasonmsg'] = reason
    ctx.obj['query'].command('clientkick', params=params)


@ts3cli.command()
@sid_option
@clid_option
@click.option(
    '--duration',
    type=int, help='ban duration in seconds (if not given permanent)'
)
@click.option('--reason', help='ban reason')
@click.pass_context
def ban(ctx, sid, clid, duration, reason):
    '''
    Ban a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    params = {
        'clid': clid
    }
    if duration:
        params['time'] = duration
    if reason:
        params['banreason'] = reason
    ctx.obj['query'].command('banclient', params=params)


@ts3cli.command()
@sid_option
@click.pass_context
def banlist(ctx, sid):
    '''
    List bans
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    click.echo(', '.join(map(
        lambda ban: '{identifier} ({banid})'.format(
            **ban,
            identifier=ban['ip'] if ban['ip']
                    else '{nickname}{uid}'.format(
                        **ban,
                        nickname=(
                            ban['lastnickname'] + '/'
                            if ban['lastnickname'] else ''
                        )
                    )
        ),
        ctx.obj['query'].command('banlist')
    )))


@ts3cli.command()
@sid_option
@click.option('--banid', help='ban id', required=True)
@click.pass_context
def bandel(ctx, sid, banid):
    '''
    Remove a ban
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    ctx.obj['query'].command('bandel', params={'banid': banid})


if __name__ == '__main__':
    ts3cli()
