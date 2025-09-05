import json

from tornado.web import authenticated

from .base import BaseAPIHandler


class ListGraderCoursesHandler(BaseAPIHandler):
    @authenticated
    async def get(self):
        user_model = self.get_current_user()
        username = user_model["name"]
        self.set_header("content-type", "application/json")
        courses = self.course_manager.list_grader_courses_for_user(username)
        self.finish(
            json.dumps(
                {
                    "user": username,
                    "courses": courses,
                }
            )
        )

class CourseMembersHandler(BaseAPIHandler):
    def _validate_grader_access(self, course_id, semester):
        """Validate that current user is a grader for the specified course.

        Returns:
            tuple: (is_valid, username) where is_valid is bool and username is str or None
        """
        user_model = self.get_current_user()
        if not user_model:
            self.set_status(401)
            self.write(
                json.dumps(
                    {
                        "status": "error",
                        "message": "Not authenticated",
                    }
                )
            )
            self.finish()
            return False, None

        username = user_model["name"]
        self.logger.warning(
            f"Validating grader access for user {username} to {course_id}-{semester}"
        )
        if not self.course_manager.is_grader_for_course(username, course_id, semester):
            self.set_status(403)
            self.write(
                json.dumps(
                    {
                        "status": "error",
                        "message": f"You are not a grader for course {course_id}-{semester}",
                    }
                )
            )
            self.finish()
            return False, None

        return True, username

    @authenticated
    async def get(self):
        course_id = self.get_argument("course_id")
        semester = self.get_argument("semester")
        is_valid, _ = self._validate_grader_access(course_id, semester)
        if not is_valid:
            return
        members = self.course_manager.get_course_members(course_id, semester)
        self.set_header("content-type", "application/json")
        self.finish(
            json.dumps(
                {
                    "course_id": course_id,
                    "semester": semester,
                    "members": members,
                }
            )
        )

    @authenticated
    async def put(self):
        data = json.loads(self.request.body)
        course_id = data.get("course_id")
        semester = data.get("semester")
        members = data.get("members")
        add_to_hub = data.get("add_to_hub", False)
        self.logger.warning(f"PUT data: {data}")
        if not course_id or not semester or not members:
            self.set_status(400)
            self.write(
                json.dumps(
                    {
                        "status": "error",
                        "message": "Missing course_id, semester, or members in request body",
                    }
                )
            )
            self.finish()
            return
        is_valid, _ = self._validate_grader_access(course_id, semester)
        if not is_valid:
            return
        updated = self.course_manager.update_course_members(course_id, semester, members)
        self.set_header("content-type", "application/json")
        if not updated:
            self.set_status(404)
            self.write(
                json.dumps(
                    {
                        "status": "error",
                        "message": f"Course {course_id}-{semester} not found or no changes made",
                    }
                )
            )
            self.finish()
            return
        added = updated.get("student_changes", {}).get("add", []) + updated.get("grader_changes", {}).get("add", [])
        if add_to_hub and added:
            # Check if users exist in JupyterHub, create them if not
            existing_users_resp = await self.api.list_users()
            existing_usernames = set(
                [u["name"] for u in json.loads(existing_users_resp.decode("utf-8"))]
            )

            missing_users = set(added) - existing_usernames
            response = await self.api.create_users(list(missing_users))
            # Check if it was a success (201), otherwise return an error
            if response:
                self.logger.warning(f"Created users in Hub: {response}")
            else:
                self.set_status(500)
                self.write(
                    json.dumps(
                        {
                            "status": "error",
                            "message": "Failed to create users in JupyterHub",
                        }
                    )
                )
                self.finish()
                return
        self.set_header("content-type", "application/json")
        self.finish(
            json.dumps(
                {
                    "status": "success",
                    "updated": updated,
                }
            )
        )

    @authenticated
    async def delete(self):
        data = json.loads(self.request.body)
        course_id = data.get("course_id")
        semester = data.get("semester")
        members = data.get("members")
        if not course_id or not semester or not members:
            self.set_status(400)
            self.write(
                json.dumps(
                    {
                        "status": "error",
                        "message": "Missing course_id, semester, or members in request body",
                    }
                )
            )
            self.finish()
            return
        is_valid, _ = self._validate_grader_access(course_id, semester)
        if not is_valid:
            return
        removed = self.course_manager.remove_course_members(course_id, semester, members)
        self.set_header("content-type", "application/json")
        self.finish(
            json.dumps(
                {
                    "removed_members": removed,
                }
            )
        )


default_handlers = [
    (r"/api/courses/?", ListGraderCoursesHandler),
    (r"/api/course_members/?", CourseMembersHandler),
]
