import datetime
import os
from importlib import metadata

import cherrypy
import genshi
import puremagic
from jaraco.context import suppress
from jaraco.functools import apply
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.util import ClassNotFound

from .template import render

BASE = os.path.abspath(os.path.dirname(__file__))


class LexerSorter:
    """
    Takes a list of preferred lexers, and sorts them at the top of the list.
    """

    def __init__(self, favored_languages):
        self.favored_langs = [x.lower().strip() for x in favored_languages]

    def sort_key_lex(self, ell):
        key = ell[0].lower()
        for f in self.favored_langs:
            if f in key:
                return 'aaaaaaaaaaaaaaaaaa' + key
        return key


class Server:
    def form(self):
        d = {}
        brand_name = cherrypy.request.app.config['branding']['name']
        add_branding(d)
        d['title'] = brand_name + " Paste"

        s = LexerSorter(cherrypy.request.app.config['lexers']['favorites'])
        lexers_in = ((ell[0], ell[1][0]) for ell in get_all_lexers())
        d['lexers'] = sorted(lexers_in, key=s.sort_key_lex)

        d['pre_nick'] = (
            ''
            if 'paste-nick' not in cherrypy.request.cookie
            else cherrypy.request.cookie['paste-nick'].value
        )
        try:
            d['short'] = bool(int(cherrypy.request.cookie['paste-short'].value))
        except KeyError:
            d['short'] = True
        return render('entry', d)

    @cherrypy.expose
    def index(self, fmt=None, nick='', code=None, file=None, makeshort=None):
        if cherrypy.request.method != 'POST':
            return self.form()
        if code is not None and not isinstance(code, str):
            # workaround for https://bitbucket.org/cherrypy/cherrypy/issue/1352
            code = code.decode('utf-8')
        ds = cherrypy.request.app.config['datastore']['datastore']
        content = dict(
            nick=nick,
            time=datetime.datetime.now(),
            makeshort=bool(makeshort),
        )
        data = file is not None and file.file is not None and file.file.read()
        if data:
            filename = file.filename
            mime = str(file.content_type)
            content.update(
                type='file',
                mime=mime,
                filename=filename,
                data=data,
            )
        else:
            content.update(
                type='code',
                fmt=fmt,
                code=code,
            )
        (uid, shortid) = ds.store(**content)

        # store cookies for 30 days
        expires = int(datetime.timedelta(days=30).total_seconds())

        if nick:
            cherrypy.response.cookie['paste-nick'] = nick
            cherrypy.response.cookie['paste-nick']['expires'] = expires

        if makeshort:
            redirid = shortid
            cherrypy.response.cookie['paste-short'] = 1
            cherrypy.response.cookie['paste-short']['expires'] = expires
        else:
            redirid = uid
            cherrypy.response.cookie['paste-short'] = 0
            cherrypy.response.cookie['paste-short']['expires'] = expires

        raise cherrypy.HTTPRedirect(
            cherrypy.url('file/' * self.as_file(content) + redirid)
        )

    @classmethod
    def as_file(cls, content):
        """
        Should the content be returned as a `file/`?
        """
        return content['type'] == 'file' and not cls.is_image(**content)

    @staticmethod
    @apply(bool)
    @suppress(puremagic.main.PureError)
    def is_image(data, filename, **kw):
        return puremagic.from_string(data, filename)

    @cherrypy.expose
    def default(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        d = {}
        add_branding(d)
        try:
            paste_data = ds.retrieve(pasteid)
        except Exception as e:
            print(e)
            raise cherrypy.NotFound(f"The paste {pasteid!r} could not be found.") from e

        if cherrypy.request.method == 'DELETE':
            ds.delete(pasteid)
            return "Deleted"

        if paste_data['type'] == 'file':
            cherrypy.response.headers['Content-Type'] = paste_data['mime']
            cherrypy.response.headers['Content-Disposition'] = (
                'inline; filename="%s"' % paste_data['filename']
            )
            cherrypy.response.headers['filename'] = paste_data['filename']
            return paste_data['data']

        total_lines = paste_data['code'].count('\n') + 1
        line_nums = map(str, range(1, total_lines + 1))
        d['linenums'] = '\n'.join(line_nums)
        if paste_data['fmt'] == '_':
            lexer = get_lexer_by_name('text')
        else:
            try:
                lexer = get_lexer_by_name(paste_data['fmt'])
            except ClassNotFound:
                lexer = get_lexer_by_name('text')
        htmlformatter = HtmlFormatter(linenos='table')
        code = highlight(paste_data['code'], lexer, htmlformatter)
        d['code'] = genshi.Markup(code)
        d['pasteid'] = pasteid
        d['plainurl'] = cherrypy.url('plain/' + pasteid)
        d['homeurl'] = cherrypy.url('')
        sid = '%s aka ' % paste_data['shortid'] if 'shortid' in paste_data else ''
        id = paste_data['uid'] if 'uid' in paste_data else pasteid
        fmt = ' (%s)' % paste_data['fmt'] if paste_data['fmt'] != '_' else ''
        nick = ' by %s' % paste_data['nick'] if 'nick' in paste_data else ''
        date = paste_data['time'].strftime('%b %d, %H:%M')
        d['title'] = f'Paste {sid}{id}{fmt}{nick} on {date}'
        return render('view', d)

    @cherrypy.expose
    def last(self, nick=''):
        ds = cherrypy.request.app.config['datastore']['datastore']
        last = ds.lookup(nick)
        if not last:
            raise cherrypy.NotFound(nick)
        raise cherrypy.HTTPRedirect(cherrypy.url('/' + last))

    @cherrypy.expose
    def plain(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        paste_data = ds.retrieve(pasteid)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return paste_data['code']

    @cherrypy.expose
    def file(self, pasteid=''):
        d = {}
        add_branding(d)
        d['title'] = "File link for %s" % pasteid
        d['link'] = cherrypy.url('/' + pasteid)
        return render('file', d)

    @cherrypy.expose
    def about(self):
        d = {}
        add_branding(d)
        d['title'] = 'About Library Paste'
        d['version'] = metadata.version('librarypaste')
        return render('about', d)


def add_branding(context):
    context.update(
        brand_name=cherrypy.request.app.config['branding']['name'],
        logo_src=cherrypy.request.app.config['branding']['logo source'],
    )
