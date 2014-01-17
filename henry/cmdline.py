from optparse import OptionParser
import datetime
import json
import os
import subprocess
import textwrap

import blessings

from henry import __version__
from henry.restapi import get_issues, get_issue_details


USAGE = '%prog [options] [command] [command-options]'
VERSION = 'henry ' + __version__

TERM = blessings.Terminal()


def git(*args):
    args = list(args)
    args.insert(0, 'git')
    return subprocess.check_output(args)


def save_cache(data):
    fn = os.path.join('.git', 'github_issues.json')
    with open(fn, 'w') as fp:
        fp.write(json.dumps(data))


def load_cache():
    fn = os.path.join('.git', 'github_issues.json')
    with open(fn, 'r') as fp:
        return json.load(fp)


def get_auth():
    path = os.path.expanduser('~/.githubauth')
    if os.path.exists(path):
        return open(path, 'r').read().strip()
    return None


def get_remote(remotename='origin'):
    # FIXME - cache this?
    remotes = git('remote', '-v').splitlines()
    remotes = [line.strip().split() for line in remotes if line.strip()]
    remotes = dict((part[0], part) for part in remotes)

    remote_url = remotes[remotename][1]
    if remote_url.startswith('git'):
        user, repo = remote_url.split(':')[1].split('/')
        repo = repo.split('.')[0]
        return user, repo

    if remote_url.startswith('https'):
        user, repo = remote_url.split('/')[-2:]
        repo = repo.split('.')[0]
        return user, repo

    raise Exception('GAH! Do not recognize url: {0}'.format(remote_url))


def indent(text):
    wrapper = textwrap.TextWrapper(
        initial_indent='    ', subsequent_indent='    ')
    return '\n'.join(['\n'.join(wrapper.wrap(block))
                      for block in text.split('\n')])


def build_parser(usage, **kwargs):
    parser = OptionParser(usage=usage, version=VERSION, **kwargs)
    parser.add_option(
        '-r', '--remote',
        dest='remote',
        metavar='REMOTE',
        help='Name of remote',
        default='origin'
    )
    return parser


def list_cmd(scriptname, cmd, argv):
    """Lists issues for current repository"""
    parser = build_parser(
        'usage: %prog list [OPTIONS]',
        description='Lists open issues',
    )

    (options, args) = parser.parse_args(argv)

    user, repo = get_remote(options.remote)
    auth = get_auth()

    if auth:
        print 'Using authentication token'

    try:
        issues_list = get_issues(user, repo, auth)
    except Exception as exc:
        print exc
        cached_data = load_cache()
        print 'Getting issue list from cache from {0} ...'.format(
            cached_data['created'])
        issues_list = cached_data['get_issues']

    print 'Issues for {0}/{1}:'.format(user, repo)
    print ''

    for issue in issues_list:
        print TERM.bold_white('#{number}: {title}'.format(
            number=str(issue['number']),
            title=issue['title']))

    return 0


def view_cmd(scriptname, cmd, argv):
    """Views a specific issue"""
    parser = build_parser(
        'usage: %prog view [OPTIONS] NUM',
        description='Views a specific issue',
    )

    (options, args) = parser.parse_args(argv)

    if not args:
        parser.print_help()
        return 1

    user, repo = get_remote(options.remote)
    auth = get_auth()

    try:
        issue_details = get_issue_details(user, repo, int(args[0]), auth)
    except Exception as exc:
        print exc
        cached_data = load_cache()
        print 'Getting issue list from cache from {0} ...'.format(
            cached_data['created'])
        issue_details = cached_data['get_issue_details'][args[0]]

    print TERM.bold_white('#{number}:  {title}'.format(
        number=str(issue_details['number']),
        title=issue_details['title']))
    print '{user} opened this issue {created}.'.format(
        user=issue_details['user']['login'],
        created=issue_details['created_at'])
    print issue_details['html_url']
    print ''
    print indent(issue_details['body'])
    print ''
    if not issue_details['comments_list']:
        print 'No comments'

    else:
        for comment in issue_details['comments_list']:
            print comment['updated_at'], comment['user']['login']
            print indent(comment['body'])
            # print comment.keys()
            print ''

    return 0


def cache_cmd(scriptname, cmd, argv):
    """Caches issue data locally"""
    parser = build_parser(
        'usage: %prog cache [OPTIONS]',
        description='Caches issue data locally',
    )

    (options, args) = parser.parse_args(argv)

    user, repo = get_remote(options.remote)

    if not '.git' in os.listdir('.'):
        print 'Please run this at the top-most level of the git clone.'
        return 1

    data = {}
    data['get_issues'] = []
    data['get_issue_details'] = {}

    print 'Getting issue list ...'
    data['get_issues'] = get_issues(user, repo)
    print '{0} issues to fetch.'.format(len(data['get_issues']))
    for issue in data['get_issues']:
        num = issue['number']
        print 'Fetching issue {0} ...'.format(num)
        data['get_issue_details'][num] = get_issue_details(
            user, repo, int(num))

    data['created'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    save_cache(data)
    print 'Data cached.'
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

    print 'Command "{0}" does not exist.'.format(command)
    print_help(scriptname)

    return 1
