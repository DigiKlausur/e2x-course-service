import { Grid, html } from "gridjs";
import "gridjs/dist/theme/mermaid.css";
import { urlJoin } from "./utils.js";
import {
  handleAddGraders,
  handleAddStudents,
  handleDeleteUser,
  handleEditUser,
  handleLoadCourseMembers,
  handleLoadCourses,
} from "./handlers.js";
import { templates } from "./templates.js";

const baseTableConfig = {
  pagination: {
    enabled: true,
    limit: 20,
    summary: true,
  },
  sort: true,
  search: true,
};

function createAddButtons(course_id, semester, grid) {
  const container = document.createElement("div");
  container.className = "table-actions-container";
  container.style.marginBottom = "10px";

  const createButton = (text, className, handler, marginLeft = false) => {
    const btn = document.createElement("button");
    btn.className = className;
    btn.textContent = text;
    if (marginLeft) btn.style.marginLeft = "10px";
    btn.onclick = () => handler(course_id, semester, grid);
    return btn;
  };

  container.append(
    createButton("Add Students", "btn add-student-btn", handleAddStudents),
    createButton("Add Graders", "btn add-grader-btn", handleAddGraders, true),
  );

  return container;
}

function initCourseTable(elementId) {
  const grid = new Grid({
    columns: [
      { id: "course_id", name: "Course ID" },
      { id: "semester", name: "Semester" },
      { id: "num_students", name: "# Students" },
      { id: "num_graders", name: "# Graders" },
      {
        id: "manage",
        name: "Manage",
        formatter: (_cell, row) => {
          const course_id = row.cells[0].data;
          const semester = row.cells[1].data;
          const url = urlJoin(
            window.APP_CONFIG.service_prefix,
            "course",
            course_id,
            semester,
          );
          return html(templates.manageButton(url));
        },
      },
    ],
    ...baseTableConfig,
    data: () => handleLoadCourses(),
  });
  grid.render(document.getElementById(elementId));
  return grid;
}

function initCourseMemberTable(elementId, course_id, semester) {
  const grid = new Grid({
    columns: [
      { id: "username", name: "Username" },
      {
        id: "grader",
        name: "Grader",
        formatter: (cell) => {
          return html(templates.checkmark(cell));
        },
      },
      {
        id: "student",
        name: "Student",
        formatter: (cell) => {
          return html(templates.checkmark(cell));
        },
      },
      {
        id: "actions",
        name: "Actions",
        formatter: (_cell, row) => {
          const username = row.cells[0].data;
          const isStudent = row.cells[2].data;
          const isGrader = row.cells[1].data;
          return html(
            templates.actionButtons(
              username,
              isStudent,
              isGrader,
              course_id,
              semester,
            ),
          );
        },
      },
    ],
    ...baseTableConfig,
    data: () => handleLoadCourseMembers(course_id, semester),
  });

  // Add buttons container above the table
  const container = document.getElementById(elementId);
  const buttonsContainer = createAddButtons(course_id, semester, grid);
  // Insert buttons before the table
  container.parentNode.insertBefore(buttonsContainer, container);

  // Event delegation for edit and delete buttons
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("edit-user-btn")) {
      const { username, student, grader, courseId, semester } =
        e.target.dataset;
      handleEditUser(
        username,
        student === "true",
        grader === "true",
        courseId,
        semester,
        grid,
      );
    }

    if (e.target.classList.contains("delete-user-btn")) {
      const { username, courseId, semester } = e.target.dataset;
      handleDeleteUser(username, courseId, semester, grid);
    }
  });

  grid.render(document.getElementById(elementId));
  return grid;
}

export const Tables = {
  initCourseTable: initCourseTable,
  initCourseMemberTable: initCourseMemberTable,
};
