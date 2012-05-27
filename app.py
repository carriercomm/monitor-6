import psutil
import os
import simplejson

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options

import uimodules

from tornado.options import define,options

define('port', default=8888, help="Run on port", type=int)

class Application(tornado.web.Application):
    def __init__(self):

        self.psutilstats = PsutilStats()

        handlers = [
            (r"/",IndexHandler),
            (r"/progress",ProgressHandler),            
            ]
        
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__),'templates'),
            static_path = os.path.join(os.path.dirname(__file__),'static'),
            ui_modules=uimodules,
            debug = True
            )
        
        tornado.web.Application.__init__(self,handlers,**settings)

class PsutilStats(object):

    def loadProgressData(self):
        progress_data = {}
        progress_data['cpu'] = [psutil.cpu_percent()]
        progress_data['memory'] = [psutil.phymem_usage().percent]
        progress_data['virtual'] = [psutil.virtmem_usage().percent]
        progress_data['disk'] = [psutil.disk_usage('/').percent]        
        return progress_data


class IndexHandler(tornado.web.RequestHandler):
    def get(self):    
    
        progress_data = self.application.psutilstats.loadProgressData();

        self.render('index.html',
                    progress_data = progress_data,
                    )             


class ProgressHandler(tornado.web.RequestHandler):
    def get(self):
        progress_data = self.application.psutilstats.loadProgressData();
        self.write(simplejson.dumps(progress_data))


if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
