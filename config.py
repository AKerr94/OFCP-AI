import os

application_config = {
    'template_path' : os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
    'database_connection' : {
        'host' : '',
        'username': '',
        'password': '',
        'database_name': ''
    }
}

cherrypy_config = {
         'global': {
                'log.screen': True,
                'log.access_file': os.path.abspath(os.path.join(os.path.dirname(__file__), 'cherrypy-access.log')),
                'log.error_file': os.path.abspath(os.path.join(os.path.dirname(__file__), 'cherrypy-error.log')),
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 8080
            },
        '/':
            {
                'environment': 'embedded',
                'tools.trailing_slash.on': True,
                'request.show_tracebacks': False,
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.encode.text_only': False,
            },
        '/static':
            {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
            },
        '/static/css':
            {
                'tools.gzip.mime_types': ['text/css']
            },
        '/static/js':
            {
                'tools.gzip.mime_types': ['application/javascript']
            }
    }
