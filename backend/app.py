import os
import logging
import tornado.ioloop
import tornado.web
from handlers import MetaHandler, SearchHandler, NodeHandler, ExpandHandler
from store import FileJsonStore
from graph_service import GraphService


WORKDIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORKDIR, "data")


def make_app() -> tornado.web.Application:
    store = FileJsonStore(DATA_DIR)
    graph_service = GraphService(store)
    return tornado.web.Application(
        [
            (r"/api/meta", MetaHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/search", SearchHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/node/(.+?)/(.+)", NodeHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/expand", ExpandHandler, dict(store=store, graph_service=graph_service)),
        ],
        debug=True,
    )


def main():
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    port = int(os.environ.get("PORT", "8000"))
    app = make_app()
    app.listen(port)
    print(f"Backend listening on http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()