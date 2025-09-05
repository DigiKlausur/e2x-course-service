import glob
import os
from collections import defaultdict
from typing import Dict, List

import pandas as pd


class CourseManager:
    def __init__(self, base_path, logger):
        self.base_path = base_path
        self.logger = logger
        self.logger.warning(f"CourseManager initialized with base_path: {self.base_path}")

    def get_courses_for_user(self, user: str):
        courses = dict(grader=defaultdict(list), student=defaultdict(list))
        search_path = os.path.join(self.base_path, "*/*/*.csv")
        for p in glob.glob(search_path):
            kind = os.path.basename(os.path.dirname(p))
            if kind not in courses:
                continue
            df = pd.read_csv(p)
            if user in df["Username"].values:
                course_name = os.path.basename(p).replace(".csv", "")
                course_id, semester = course_name.split("-", 1)
                courses[kind][course_id].append(semester)
        # Sort semesters for each course
        for kind in courses:
            for course_id in courses[kind]:
                courses[kind][course_id] = sorted(courses[kind][course_id])
        return courses

    def list_grader_courses_for_user(self, user: str):
        courses = []
        # For each course put the course_id, semester, number of graders, number of students
        search_path = os.path.join(self.base_path, "*/grader/*.csv")
        for p in glob.glob(search_path):
            df = pd.read_csv(p)
            if user in df["Username"].values:
                course_name = os.path.basename(p).replace(".csv", "")
                course_id, semester = course_name.split("-", 1)
                num_graders = len(df)
                # Get number of students
                students_file = os.path.join(
                    self.base_path, course_id, "student", f"{course_id}-{semester}.csv"
                )
                if os.path.exists(students_file):
                    df_students = pd.read_csv(students_file)
                    num_students = len(df_students)
                else:
                    num_students = 0
                courses.append(
                    {
                        "course_id": course_id,
                        "semester": semester,
                        "num_graders": num_graders,
                        "num_students": num_students,
                    }
                )
        return courses

    def is_grader_for_course(self, user: str, course_id: str, semester: str):
        graders_file = os.path.join(
            self.base_path, course_id, "grader", f"{course_id}-{semester}.csv"
        )
        if not os.path.exists(graders_file):
            self.logger.error(f"Graders file {graders_file} does not exist.")
            return False
        df = pd.read_csv(graders_file)
        return user in df["Username"].values

    def get_members_file(self, course_id: str, semester: str, kind: str):
        if kind not in ["student", "grader"]:
            self.logger.error(f"Invalid kind {kind} for getting members file.")
            return None
        members_file = os.path.join(self.base_path, course_id, kind, f"{course_id}-{semester}.csv")
        if not os.path.exists(members_file):
            self.logger.error(f"Members file {members_file} does not exist.")
            return None
        return members_file

    def get_course_members(self, course_id: str, semester: str) -> Dict[str, List[str]]:
        graders = []
        students = []
        graders_file = self.get_members_file(course_id, semester, kind="grader")
        if graders_file:
            df_graders = pd.read_csv(graders_file)
            graders = df_graders["Username"].tolist()
        students_file = self.get_members_file(course_id, semester, kind="student")
        if students_file:
            df_students = pd.read_csv(students_file)
            students = df_students["Username"].tolist()
        # Return a dict with username as key and roles as values
        members = defaultdict(list)
        for g in graders:
            members[g].append("grader")
        for s in students:
            members[s].append("student")
        return members

    def update_course_members(self, course_id: str, semester: str, members: Dict[str, List[str]]):
        current_members = self.get_course_members(course_id, semester)
        student_changes = {"add": [], "remove": []}
        grader_changes = {"add": [], "remove": []}
        # Determine changes
        for username, roles in members.items():
            current_roles = set(current_members.get(username, []))
            new_roles = set(roles)
            if "student" in new_roles and "student" not in current_roles:
                student_changes["add"].append(username)
            if "student" not in new_roles and "student" in current_roles:
                student_changes["remove"].append(username)
            if "grader" in new_roles and "grader" not in current_roles:
                grader_changes["add"].append(username)
            if "grader" not in new_roles and "grader" in current_roles:
                grader_changes["remove"].append(username)
        # Apply changes
        if student_changes["add"]:
            self.add_members_to_course(student_changes["add"], course_id, semester, kind="student")
        if student_changes["remove"]:
            self.remove_members_from_course(
                student_changes["remove"], course_id, semester, kind="student"
            )
        if grader_changes["add"]:
            self.add_members_to_course(grader_changes["add"], course_id, semester, kind="grader")
        if grader_changes["remove"]:
            self.remove_members_from_course(
                grader_changes["remove"], course_id, semester, kind="grader"
            )
        return {
            "student_changes": student_changes,
            "grader_changes": grader_changes,
        }

    def remove_course_members(self, course_id: str, semester: str, members: List[str]):
        graders = self.remove_members_from_course(members, course_id, semester, kind="grader")
        students = self.remove_members_from_course(members, course_id, semester, kind="student")
        return {"removed_students": students, "removed_graders": graders}

    def add_members_to_course(self, members: List[str], course_id: str, semester: str, kind: str):
        if kind not in ["student", "grader"]:
            self.logger.error(f"Invalid kind {kind} for adding members.")
            return []
        members_files = os.path.join(self.base_path, course_id, kind, f"{course_id}-{semester}.csv")
        if not os.path.exists(members_files):
            self.logger.error(f"Members file {members_files} does not exist.")
            return []
        df = pd.read_csv(members_files)
        existing_members = set(df["Username"].values)
        new_members = [m.strip() for m in members if m not in existing_members]
        if not new_members:
            return []
        new_df = pd.DataFrame(new_members, columns=["Username"])
        updated_df = pd.concat([df, new_df], ignore_index=True)
        updated_df.to_csv(members_files, index=False)
        return new_members

    def remove_members_from_course(
        self, members: List[str], course_id: str, semester: str, kind: str
    ):
        if kind not in ["student", "grader"]:
            self.logger.error(f"Invalid kind {kind} for removing members.")
            return []
        members_file = os.path.join(self.base_path, course_id, kind, f"{course_id}-{semester}.csv")
        if not os.path.exists(members_file):
            self.logger.error(f"Members file {members_file} does not exist.")
            return []
        df = pd.read_csv(members_file)
        existing_members = set(df["Username"].values)
        members_to_remove = [m.strip() for m in members if m in existing_members]
        if not members_to_remove:
            return []
        updated_df = df[~df["Username"].isin(members_to_remove)]
        updated_df.to_csv(members_file, index=False)
        return members_to_remove
