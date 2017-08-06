# -*- coding: utf-8 -*-
from datetime import timedelta

import click
from ts3py import TS3Error, TS3Query

from .utils import (cid_option, clid_option, count_to_str, msg_option,
                    pass_query, sid_option, use)


@click.group()
@click.option('--host', help='teamspeak query host', default='localhost')
@click.option(
    '--port', type=int, help='teamspeak query port', default=10011,
)
@click.option('--username', help='query username', default='serveradmin')
@click.option('--password', help='query password', required=True)
@click.pass_context
def ts3cli(ctx, host, port, username, password):
    query = TS3Query(host, port)
    query.login(username, password)
    ctx.obj = query


@ts3cli.resultcallback()
@pass_query
def disconnect(query, *args, **kwargs):
    # disconnect from query
    query.command('quit')


@ts3cli.command()
@click.option(
    '--hide-offline', help='hide offline servers',
    is_flag=True, default=False
)
@pass_query
def server(query, hide_offline):
    '''
    List virtual servers
    '''
    serverlist = query.command('serverlist')
    if hide_offline:
        serverlist = filter(
            lambda vs: vs['virtualserver_status'] == 'online', serverlist
        )
    click.echo(', '.join(map(
        lambda vs: u'{name} ({virtualserver_id}){clientsonline}'.format(
            name=(
                vs['virtualserver_name']
                if vs['virtualserver_status'] == 'online'
                else click.style(vs['virtualserver_name'], fg='red')
            ),
            clientsonline=' - {} online'.format(count_to_str(
                vs['virtualserver_clientsonline'], 'client'
            )) if vs['virtualserver_status'] == 'online' else '',
            **vs
        ),
        serverlist
    )))


@ts3cli.command()
@sid_option
@pass_query
def serverstart(query, sid):
    '''
    Start a server
    '''
    query.command('serverstart', params={'sid': sid})


@ts3cli.command()
@sid_option
@pass_query
def serverstop(query, sid):
    '''
    Stop a server
    '''
    query.command('serverstop', params={'sid': sid})


@ts3cli.command()
@msg_option
@pass_query
def gm(query, msg):
    '''
    Send a global message
    '''
    query.command('gm', params={'msg': msg})


@ts3cli.command()
@sid_option
@pass_query
@click.option('--cid', help='limit to clients in this channel', type=int)
@click.option(
    '--near',
    help='limit to clients in the same channel as given client', type=int
)
@click.option('--show-query', help='show query clients', is_flag=True)
def clients(query, sid, cid, near, show_query):
    '''
    List clients on a virtual server
    '''
    use(query, sid)
    clientlist = query.command('clientlist')
    if not show_query:
        clientlist = filter(lambda c: c['client_type'] == 0, clientlist)
    if near:
        # find cid of client
        cid = query.command('clientinfo', params={'clid': near})[0]['cid']
    if cid:
        clientlist = filter(lambda c: c['cid'] == cid, clientlist)
    click.echo(', '.join(map(
        lambda client: u'{client_nickname} ({clid})'.format(**client),
        clientlist
    )))


@ts3cli.command()
@sid_option
@clid_option
@pass_query
def clientinfo(query, sid, clid):
    '''
    View detailed information about a client
    '''
    use(query, sid)
    client_info = query.command(
        'clientinfo', params={'clid': clid})[0]
    click.echo(
        u'''Nickname: {client_nickname}
Description: {client_description}
ID: {clid}
Database ID: {client_database_id}
Unique Identifier: {client_unique_identifier}
Version/Platform: {client_version} on {client_platform}
IP: {connection_client_ip}
Country: {client_country}
Connection time: {connection_time}
Channel (ID): {cid}
Microphone/Speaker: {microphone}  {speaker}'''.format(
            clid=clid, connection_time=timedelta(
                milliseconds=client_info['connection_connected_time']),
            microphone=click.style(
                '🎙', fg='green' if client_info['client_is_talker'] else None,
                bg='red' if client_info['client_input_muted'] or
                not client_info['client_input_hardware'] else None
            ),
            speaker=click.style(
                '🔈', bg='red' if client_info['client_output_muted'] or
                not client_info['client_output_hardware'] else None
            ),
            **client_info
        )
    )


@ts3cli.command()
@sid_option
@pass_query
def channel(query, sid):
    '''
    List channel on a virtual server
    '''
    use(query, sid)
    click.echo(', '.join(map(
        lambda channel: u'{channel_name} ({cid}){clients}'.format(
            clients=' - {}'.format(
                count_to_str(channel['total_clients'], 'client')
            ) if channel['total_clients'] >= 1 else '',
            **channel
        ),
        query.command('channellist')
    )))


@ts3cli.command()
@sid_option
@cid_option
@pass_query
def channelinfo(query, sid, cid):
    '''
    View detailed information about a channel
    '''
    use(query, sid)
    channel_info = query.command(
        'channelinfo', params={'cid': cid})[0]
    parent = query.command(
        'channelinfo', params={'cid': channel_info['pid']}
    )[0]['channel_name'] if 'pid' in channel_info else None
    click.echo(
        u'''Name: {channel_name}
Topic: {channel_topic}
Description: {channel_description}
Password: {password}
Type: {type}
Max clients: {maxclients}
Filepath: {channel_filepath}
Icon: {channel_icon_id}
Parent: {parent}'''.format(
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
            ]))[0][0],
            parent=parent,
            **channel_info
        )
    )


@ts3cli.command()
@sid_option
@click.option('--name', help='name of the new channel')
@click.option('--permanent', help='make the channel permanent', is_flag=True)
@pass_query
def channelcreate(query, sid, name, permanent):
    '''
    Create a channel
    '''
    use(query, sid)
    params = {'channel_name': name}
    if permanent:
        params['channel_flag_permanent'] = 1
    response = query.command('channelcreate', params=params)
    click.echo('Created "{}" ({})'.format(name, response[0]['cid']))


@ts3cli.command()
@sid_option
@clid_option
@msg_option
@pass_query
def poke(query, sid, clid, msg):
    '''
    Poke a client
    '''
    use(query, sid)
    query.command('clientpoke', params={'clid': clid, 'msg': msg})


@ts3cli.command()
@sid_option
@clid_option
@click.option('--reason', help='kick reason')
@click.option(
    '--channel', help='kick from channel', is_flag=True, default=False
)
@pass_query
def kick(query, sid, clid, reason, channel):
    '''
    Kick a client
    '''
    use(query, sid)
    params = {
        'clid': clid,
        'reasonid': 4 if channel else 5
    }
    if reason:
        params['reasonmsg'] = reason
    query.command('clientkick', params=params)


@ts3cli.command()
@sid_option
@clid_option
@cid_option
@click.option('--password', help='password of the target channel')
@pass_query
def move(query, sid, clid, cid, password):
    '''
    Move a client to another channel
    '''
    use(query, sid)
    params = {
        'clid': clid,
        'cid': cid,
    }
    if password:
        params['cpw'] = password
    query.command('clientmove', params=params)


@ts3cli.command()
@sid_option
@clid_option
@click.option(
    '--duration',
    type=int, help='ban duration in seconds (if not given permanent)'
)
@click.option('--reason', help='ban reason')
@pass_query
def ban(query, sid, clid, duration, reason):
    '''
    Ban a client
    '''
    use(query, sid)
    params = {
        'clid': clid
    }
    if duration:
        params['time'] = duration
    if reason:
        params['banreason'] = reason
    query.command('banclient', params=params)


@ts3cli.command()
@sid_option
@pass_query
def banlist(query, sid):
    '''
    List bans
    '''
    use(query, sid)
    click.echo(', '.join(map(
        lambda ban: '{identifier} ({banid})'.format(
            identifier=ban['ip'] if ban['ip']
                    else u'{nickname}{uid}'.format(
                        nickname=(
                            ban['lastnickname'] + '/'
                            if ban['lastnickname'] else ''
                        ),
                        **ban
                    ),
            **ban
        ),
        query.command('banlist')
    )))


@ts3cli.command()
@sid_option
@click.option('--banid', help='ban id', required=True)
@pass_query
def bandel(query, sid, banid):
    '''
    Remove a ban
    '''
    use(query, sid)
    query.command('bandel', params={'banid': banid})


@ts3cli.command()
@sid_option
@click.option('--cldbid', help='target client (database id)')
@pass_query
def complaints(query, sid, cldbid):
    '''
    List complaints
    '''
    use(query, sid)
    complaintlist = []
    try:
        complaintlist = query.command(
            'complainlist', params={'tcldbid': cldbid} if cldbid else {}
        )
    except TS3Error as e:
        if e.error_id == 1281:
            # empty result set
            click.echo('There are no complaints on this server.')
            return
        else:
            raise e
    click.echo('\n'.join(
        map(
            lambda complaint:
                '{fname} ({fcldbid}) -> {tname} ({tcldbid}): {message}'.format(
                    **complaint
                ),
            complaintlist
        )
    ))


@ts3cli.command()
@sid_option
@click.option('--fromcl', help='from client (database id)', required=True)
@click.option('--tocl', help='to client (database id)', required=True)
@pass_query
def complaintdel(query, sid, fromcl, tocl):
    '''
    Delete a complaint
    '''
    use(query, sid)
    query.command('complaindel', params={
        'fcldbid': fromcl,
        'tcldbid': tocl
    })
    click.echo('Successfully removed complaint.')


@ts3cli.command()
@sid_option
@click.option('--cldbid', help='target client (database id)', required=True)
@pass_query
def complaintdelall(query, sid, cldbid):
    '''
    Delete all complaints for a specific client
    '''
    use(query, sid)
    query.command('complaindelall', params={'tcldbid': cldbid})
    click.echo('Successfully removed all complaints for {}.'.format(cldbid))


if __name__ == '__main__':
    ts3cli()
