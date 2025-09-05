import os

from jinja2 import Environment, FileSystemLoader
from jupyterhub.services.auth import (
    HubOAuth,
    HubOAuthCallbackHandler,
)
from jupyterhub.utils import url_path_join as ujoin
from tornado import web
from tornado.httpclient import AsyncHTTPClient
from traitlets import Any, Dict, Integer, List, Unicode
from traitlets.config import Application

from ._data import DATA_FILES_PATH
from .course_manager import CourseManager
from .handlers import apihandlers, handlers
from .hub_api import HubAPI


class CourseServiceApp(Application):
    data_files_path = Unicode(
        DATA_FILES_PATH, help="Path to the data files for the application"
    ).tag(config=True)

    tornado_settings = Dict(help="Tornado settings for the application").tag(config=True)

    template_path = Unicode(
        os.path.join(DATA_FILES_PATH, "templates"),
        help="Path to the Jinja2 templates for the application",
    )

    static_path = Unicode(
        os.path.join(DATA_FILES_PATH, "static"),
        help="Path to the static files for the application",
    )

    handlers = List(
        help="List of (url, handler) tuples for the application",
    )

    service_prefix = Unicode(
        os.environ.get("JUPYTERHUB_SERVICE_PREFIX"), help="The URL prefix for the service"
    )

    api_token = Unicode(
        os.environ.get("JUPYTERHUB_API_TOKEN"),
        help="The API token for the service to authenticate with JupyterHub",
    )

    course_base_path = Unicode(
        help="The base path where course data is stored",
    ).tag(config=True)

    http_client = Any(AsyncHTTPClient(), help="The HTTP client for making requests to JupyterHub")

    tornado_application = Any(help="The Tornado application instance")

    port = Integer(10101, help="The port for the service to listen on").tag(config=True)

    def init_tornado_settings(self):
        jinja_env = Environment(loader=FileSystemLoader(self.template_path))
        hub = HubOAuth(api_token=self.api_token)
        hub_api = HubAPI(hub)
        settings = {
            "jinja2_env": jinja_env,
            "service_prefix": self.service_prefix,
            "http_client": self.http_client,
            "hub_auth": hub,
            "hub_api": hub_api,
            "cookie_secret": os.urandom(32),
            "course_manager": CourseManager(
                base_path=os.path.abspath(self.course_base_path),
                logger=self.log,
            ),
            "logger": self.log,
        }
        self.tornado_settings = settings

    def init_handlers(self):
        app_handlers = [
            (
                ujoin(self.service_prefix, "static", "(.*)"),
                web.StaticFileHandler,
                {"path": self.static_path},
            ),
            (
                ujoin(self.service_prefix, "oauth_callback"),
                HubOAuthCallbackHandler,
            ),
        ]
        for pattern, handler in apihandlers.default_handlers + handlers.default_handlers:
            full_pattern = ujoin(self.service_prefix, pattern.lstrip("/"))
            app_handlers.append((full_pattern, handler))
        self.handlers = app_handlers

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.init_tornado_settings()
        self.init_handlers()
        self.initialize_tornado_application()

    def initialize_tornado_application(self):
        self.tornado_application = web.Application(self.handlers, **self.tornado_settings)

    def start(self):
        self.log.warning(f"Starting Course Service on port {self.port}")
        self.tornado_application.listen(self.port)
        import asyncio

        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    CourseServiceApp.launch_instance()
