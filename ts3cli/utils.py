import click

sid_option = click.option('--sid', help='virtual server id', default=1)
cid_option = click.option('--cid', help='channel id', required=True)
clid_option = click.option('--clid', help='client id', required=True)
msg_option = click.option('--msg', help='message', required=True)


def count_to_str(count, word):
    '''
    Merge count and word with (or without) plural ending

    :type count: int
    :type word: str

    :rtype: str
    '''
    return ' '.join((str(count), word + 's' if count > 1 else word))
