from tornado.web import authenticated

from .base import BaseTemplateHandler


class HomeHandler(BaseTemplateHandler):
    @authenticated
    async def get(self):
        self.render_template("index.j2")


class ManageCourseHandler(BaseTemplateHandler):
    @authenticated
    async def get(self, course_id, semester):
        self.render_template("manage_course.j2", course_id=course_id, semester=semester)


default_handlers = [
    (r"/?", HomeHandler),
    (r"/course/([^/]+)/([^/]+)/?", ManageCourseHandler),
]
