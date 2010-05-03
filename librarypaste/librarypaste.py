#!/usr/bin/env python
# encoding: utf-8

import os
import cherrypy
from pastebin import PasteBinPage, PasteViewPage, LastPage, PastePlainPage

mapper = cherrypy.dispatch.RoutesDispatcher()
mapper.connect('paste', '', PasteBinPage())
mapper.connect('viewpaste', ':pasteid', PasteViewPage())
mapper.connect('plain', 'plain/:pasteid', PastePlainPage())
mapper.connect('last', 'last/:nick', LastPage())
mapper.connect('static_resource', 'static/:resource', PasteViewPage())

# Cherrypy configuration here
app_conf = {
	'/' : {'request.dispatch' : mapper},
	'/static' : {
		'tools.staticdir.on' : True,
		'tools.staticdir.dir' : os.path.abspath('static'),
	}
}


if __name__ == "__main__":
    cherrypy.tree.mount(root=None, config=app_conf)
    cherrypy.quickstart(None, '', config=app_conf)


