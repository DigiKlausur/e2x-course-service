from jupyterhub.services.auth import HubOAuthenticated
from jupyterhub.utils import url_path_join as ujoin
from tornado.web import RequestHandler

from ..course_manager import CourseManager
from ..hub_api import HubAPI


class BaseHandler(HubOAuthenticated, RequestHandler):
    @property
    def course_manager(self) -> CourseManager:
        return self.settings["course_manager"]

    @property
    def logger(self):
        return self.settings["logger"]


class BaseTemplateHandler(BaseHandler):
    def render_template(self, template_name, **kwargs):
        jinja_env = self.settings["jinja2_env"]
        template = jinja_env.get_template(template_name)
        user_model = self.get_current_user()
        if user_model:
            kwargs["user"] = user_model.get("name")
        else:
            kwargs["user"] = None
        # Add any common template variables here
        kwargs.update(
            {
                "base_url": self.settings.get("base_url", "/"),
                "service_prefix": self.settings.get("service_prefix", "/"),
                "api_url": ujoin(self.settings.get("service_prefix", "/"), "api"),
                "static_url": self.settings.get("static_url"),
                "hub_url": self.settings.get("hub_url", "/hub/"),
            }
        )
        self.write(template.render(**kwargs))


class BaseAPIHandler(BaseHandler):
    @property
    def api(self) -> HubAPI:
        return self.settings["hub_api"]
