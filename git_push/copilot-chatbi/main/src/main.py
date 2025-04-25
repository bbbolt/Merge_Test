import tornado
import tornado.ioloop
import tornado.web

from handler import UploadHandler, QueryHandler

import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from report import glo_asyn_report_thread, async_report_log


def make_app():
    return tornado.web.Application([
        (r"/upload", UploadHandler),
        (r"/query", QueryHandler),
    ])

if __name__ == "__main__":
    glo_asyn_report_thread.daemon = True
    glo_asyn_report_thread.start()
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()