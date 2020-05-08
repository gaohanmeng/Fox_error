class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            text = '%s===%s' % (environ['PATH_INFO'], self.prefix)
            # return ["This url does not belong to the app.".encode()]
            return [text.encode()]


def main():
    midd = PrefixMiddleware(None, '/test/')


if __name__ == "__main__":
    main()
