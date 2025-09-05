export const templates = {
  manageButton: (url) =>
    `<a href="${url}" class="gridjs-btn manage-btn">Manage</a>`,

  checkmark: (condition) => (condition ? "✓" : ""),

  actionButtons: (username, isStudent, isGrader, courseId, semester) => `
        <div class="action-buttons">
            <button class="gridjs-btn edit-user-btn" 
                    data-username="${username}" 
                    data-student="${isStudent}" 
                    data-grader="${isGrader}"
                    data-course-id="${courseId}"
                    data-semester="${semester}"
                    onclick="window.editUser('${username}', ${isStudent}, ${isGrader}, '${courseId}', '${semester}')">
                Edit
            </button>
            <button class="gridjs-btn delete-user-btn" 
                    data-username="${username}" 
                    data-course-id="${courseId}"
                    data-semester="${semester}"
                    onclick="window.deleteUser('${username}', '${courseId}', '${semester}')">
                Delete
            </button>
        </div>
    `,
};
