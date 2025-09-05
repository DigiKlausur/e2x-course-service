import { API } from "./api.js";
import {
  showAddUsersModal,
  showErrorModal,
  requestConfirmation,
  requestTextConfirmation,
  showEditUserModal,
  showSuccessModal,
} from "./modals.js";

export async function handleAddStudents(courseId, semester, grid) {
  const usernames = await showAddUsersModal(
    "Add Students",
    "student1\nstudent2\nstudent3",
  );

  if (!usernames) return;
  if (usernames.length === 0) {
    await showErrorModal("No usernames provided.");
    return;
  }

  try {
    await API.courses.members.update(
      courseId,
      semester,
      Object.fromEntries(usernames.map((u) => [u, ["student"]])),
      true,
    );
    console.log("Refreshing table", grid);
    grid.forceRender();
    await showSuccessModal(
      `Successfully added ${usernames.length} students to the course.`,
    );
  } catch (error) {
    console.error("Error adding students:", error);
    await showErrorModal("Error adding students: " + error.message);
  }
}

export async function handleAddGraders(courseId, semester, grid) {
  const usernames = await showAddUsersModal(
    "Add Graders",
    "grader1\ngrader2\ngrader3",
  );

  if (!usernames) return;
  if (usernames.length === 0) {
    await showErrorModal("No usernames provided.");
    return;
  }

  try {
    await API.courses.members.update(
      courseId,
      semester,
      Object.fromEntries(usernames.map((u) => [u, ["grader"]])),
      true,
    );
    grid.forceRender();
    await showSuccessModal(
      `Successfully added ${usernames.length} graders to the course.`,
    );
  } catch (error) {
    console.error("Error adding graders:", error);
    await showErrorModal("Error adding graders: " + error.message);
  }
}

export async function handleDeleteUser(username, courseId, semester, grid) {
  try {
    let confirmed = false;
    if (username === window.APP_CONFIG.user) {
      confirmed = await requestTextConfirmation(
        `You are about to remove yourself from this course. This will affect your access.<br><br>To confirm, please type your username:`,
        username,
      );
    } else {
      confirmed = await requestConfirmation(
        `Are you sure you want to remove ${username} from this course?`,
        "Remove User",
      );
    }
    if (!confirmed) return;

    await API.courses.members.delete(courseId, semester, [username]);
    grid.forceRender();
  } catch (error) {
    console.error("Error deleting user:", error);
    await showErrorModal("Error updating user: " + error.message);
  }
}

export async function handleEditUser(
  username,
  isStudent,
  isGrader,
  courseId,
  semester,
  grid,
) {
  const newRoles = await showEditUserModal(username, isStudent, isGrader);

  if (!newRoles) return; // User cancelled or validation failed

  if (
    username === window.APP_CONFIG.user &&
    isGrader &&
    !newRoles.includes("grader")
  ) {
    const confirmed = await requestTextConfirmation(
      `You are about to remove your own grader role. This will affect your access.<br><br>To confirm, please type your username:`,
      username,
    );
    if (!confirmed) return;
  }

  try {
    await API.courses.members.update(courseId, semester, {
      [username]: newRoles,
    });
    grid.forceRender();
  } catch (err) {
    await showErrorModal("Error updating user: " + err.message);
  }
}

export async function handleLoadCourseMembers(courseId, semester) {
  try {
    const data = await API.courses.members.list(courseId, semester);
    return Object.entries(data.members).map(([username, roles]) => ({
      username: username,
      student: roles && roles.includes("student"),
      grader: roles && roles.includes("grader"),
      edit: null, // Placeholder for edit column
    }));
  } catch (error) {
    await showErrorModal("Error fetching course members: " + error);
    return [];
  }
}

export async function handleLoadCourses() {
  try {
    const data = await API.courses.list();
    return data.courses.sort((a, b) => {
      const courseCmp = a.course_id.localeCompare(b.course_id);
      if (courseCmp !== 0) return courseCmp;

      // Custom semester sorting: digits first, then letters (for format like "WS24", "SS25")
      const semesterA = a.semester;
      const semesterB = b.semester;

      // Check if semester follows the pattern: 2 letters + 2 digits
      const semesterPattern = /^([A-Za-z]{2})(\d{2})$/;
      const matchA = semesterA.match(semesterPattern);
      const matchB = semesterB.match(semesterPattern);

      if (matchA && matchB) {
        // Both follow the pattern, sort by digits first (descending), then letters
        const digitsA = matchA[2];
        const digitsB = matchB[2];
        const lettersA = matchA[1];
        const lettersB = matchB[1];

        const digitsCmp = -digitsA.localeCompare(digitsB); // Negative for descending
        if (digitsCmp !== 0) return digitsCmp;
        return -lettersA.localeCompare(lettersB); // Negative for descending
      } else {
        // Fallback to original sorting if pattern doesn't match
        return -semesterA.localeCompare(semesterB);
      }
    });
  } catch (error) {
    await showErrorModal("Error fetching courses: " + error);
    return [];
  }
}
