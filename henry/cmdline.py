from optparse import OptionParser
import subprocess
import textwrap

import blessings

from henry import __version__
from henry.restapi import API


USAGE = '%prog [options] [command] [command-options]'
VERSION = 'henry ' + __version__

TERM = blessings.Terminal()


def git(*args):
    args = list(args)
    args.insert(0, 'git')
    return subprocess.check_output(args)


def get_remote(remotename='origin'):
    # FIXME - cache this?
    remotes = git('remote', '-v').splitlines()
    remotes = [line.strip().split() for line in remotes if line.strip()]
    remotes = dict((part[0], part) for part in remotes)

    # Return the url
    return remotes[remotename][1]


def indent(text):
    wrapper = textwrap.TextWrapper(
        initial_indent='    ', subsequent_indent='    ')
    return '\n'.join(['\n'.join(wrapper.wrap(block)) for block in text.split('\n')])


def build_parser(usage, **kwargs):
    return OptionParser(usage=usage, version=VERSION, **kwargs)


def list_cmd(scriptname, cmd, argv):
    """Lists issues for current repository"""
    parser = build_parser(
        'usage: %prog list [OPTIONS]',
        description='Lists open issues',
    )
    parser.add_option(
        '-r', '--remote',
        dest='remote',
        metavar='REMOTE',
        help='Name of remote',
        default='origin'
    )

    (options, args) = parser.parse_args(argv)

    remote_url = get_remote(options.remote)
    if remote_url.startswith('git'):
        user, repo = remote_url.split(':')[1].split('/')
        repo = repo.split('.')[0]
    else:
        print 'GAH! Do not recognize url: {0}'.format(remote_url)
        return 1

    repo_api = API('https://api.github.com/repos/{user}/{repo}'.format(
        user=user, repo=repo))

    issues = repo_api.issues.get().json()
    for issue in issues:
        print TERM.bold_white('#{number}: {title}'.format(
            number=str(issue['number']),
            title=issue['title']))

    return 0


def view_cmd(scriptname, cmd, argv):
    """Views a specific issue"""
    parser = build_parser(
        'usage: %prog list [OPTIONS]',
        description='Views a specific issue',
    )
    parser.add_option(
        '-r', '--remote',
        dest='remote',
        metavar='REMOTE',
        help='Name of remote',
        default='origin'
    )

    (options, args) = parser.parse_args(argv)

    if not args:
        parser.print_help()
        return 1

    remote_url = get_remote(options.remote)
    if remote_url.startswith('git'):
        user, repo = remote_url.split(':')[1].split('/')
        repo = repo.split('.')[0]
    else:
        print 'GAH! Do not recognize url: {0}'.format(remote_url)
        return 1

    repo_api = API('https://api.github.com/repos/{user}/{repo}'.format(
        user=user, repo=repo))

    issue = repo_api.issues(int(args[0])).get().json()
    print TERM.bold_white('#{number}:  {title}'.format(
        number=str(issue['number']),
        title=issue['title']))
    print '{user} opened this issue {created}.'.format(
        user=issue['user']['login'],
        created=issue['created_at'])
    print issue['html_url']
    print ''
    print indent(issue['body'])
    print ''
    if not issue['comments']:
        print 'No comments'

    else:
        comments_api = API('https://api.github.com/repos/{user}/{repo}/issues/{num}'.format(
            user=user, repo=repo, num=int(args[0])))

        for comment in comments_api.comments.get().json():
            print comment['updated_at'], comment['user']['login']
            print indent(comment['body'])
            # print comment.keys()
            print ''

    return 0


def get_handlers():
    handlers = [(name.replace('_cmd', ''), fun, fun.__doc__)
                for name, fun in globals().items()
                if name.endswith('_cmd')]
    return handlers


def print_help(scriptname):
    print '%s version %s' % (scriptname, __version__)

    handlers = get_handlers()

    parser = build_parser("%prog [command]")
    parser.print_help()
    print ''
    print 'Commands:'
    for command_str, _, command_help in handlers:
        print '  {cmd:10}  {hlp}'.format(cmd=command_str, hlp=command_help)


def cmdline_handler(scriptname, argv):
    handlers = get_handlers()

    if not argv or argv[0] in ('-h', '--help'):
        print_help(scriptname)
        return 0

    if '--version' in argv:
        # We've already printed the version, so we can just exit.
        return 0

    command = argv.pop(0)
    for (cmd, fun, hlp) in handlers:
        if cmd == command:
            return fun(scriptname, command, argv)

    err('Command "{0}" does not exist.'.format(command))
    print_help(scriptname)

    return 1
