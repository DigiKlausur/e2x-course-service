import Swal from "sweetalert2/dist/sweetalert2.js"; // smaller core, no icons/animations
import "sweetalert2/dist/sweetalert2.css"; // CSS separately

/** =============================
 * Add Users Modal
 * Returns an array of usernames, or null if cancelled
 * ============================== */
export function showAddUsersModal(
  title = "Add Users",
  placeholder = "username1\nusername2\nusername3",
) {
  return Swal.fire({
    title,
    html: `<textarea id="swal-usernames" class="swal2-textarea" placeholder="${placeholder}" rows="10"></textarea>`,
    showCancelButton: true,
    confirmButtonText: "Add Users",
    cancelButtonText: "Cancel",
    animation: false,
    preConfirm: () => {
      const textarea = Swal.getPopup().querySelector("#swal-usernames");
      const usernamesText = textarea.value.trim();
      if (!usernamesText) return [];
      return usernamesText
        .split("\n")
        .map((u) => u.trim())
        .filter((u) => u.length > 0);
    },
    didOpen: () => {
      Swal.getPopup().querySelector("#swal-usernames").focus();
    },
  }).then((result) => (result.isConfirmed ? result.value : null));
}

/** =============================
 * Alert Modal
 * ============================== */
export function showErrorModal(message, title = "Error") {
  return Swal.fire({
    icon: "error",
    title,
    html: message,
    confirmButtonText: "OK",
    animation: false,
  });
}

/** =============================
 * Success Alert Modal
 * ============================== */
export function showSuccessModal(message, title = "Success") {
  return Swal.fire({
    icon: "success",
    title,
    html: message,
    confirmButtonText: "OK",
    animation: false,
  });
}
/** =============================
 * Confirm Modal
 * Returns true if confirmed, false otherwise
 * ============================== */
export function requestConfirmation(message, confirmText = "Confirm") {
  return Swal.fire({
    icon: "question",
    title: "Confirmation",
    html: message,
    showCancelButton: true,
    confirmButtonText: confirmText,
    cancelButtonText: "Cancel",
    animation: false,
  }).then((result) => result.isConfirmed);
}

/** =============================
 * Prompt Confirm Modal (requires exact text)
 * Returns true if the correct text was entered
 * ============================== */
export function requestTextConfirmation(message, requiredText) {
  return Swal.fire({
    icon: "warning",
    title: "Confirmation Required",
    html: `
      <p>${message}</p>
      <input type="text" id="swal-prompt-input" class="swal2-input" placeholder="Type here...">
    `,
    showCancelButton: true,
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    animation: false,
    didOpen: () => {
      const input = Swal.getPopup().querySelector("#swal-prompt-input");
      input.addEventListener("input", () => {
        Swal.getConfirmButton().disabled = input.value !== requiredText;
      });
      input.focus();
      Swal.getConfirmButton().disabled = true;
    },
  }).then((result) => result.isConfirmed);
}

/** =============================
 * Edit User Modal
 * Returns the array of selected roles, or null if cancelled
 * ============================== */
export function showEditUserModal(username, isStudent, isGrader) {
  const checkboxHtml = `
    <label><input type="checkbox" id="swal-student" ${isStudent ? "checked" : ""}> Student</label><br>
    <label><input type="checkbox" id="swal-grader" ${isGrader ? "checked" : ""}> Grader</label>
  `;

  return Swal.fire({
    title: `Edit User: ${username}`,
    html: checkboxHtml,
    showCancelButton: true,
    confirmButtonText: "Save",
    cancelButtonText: "Cancel",
    animation: false,
    preConfirm: () => {
      const newIsStudent =
        Swal.getPopup().querySelector("#swal-student").checked;
      const newIsGrader = Swal.getPopup().querySelector("#swal-grader").checked;

      const newRoles = [];
      if (newIsStudent) newRoles.push("student");
      if (newIsGrader) newRoles.push("grader");

      if (newRoles.length === 0) {
        Swal.showValidationMessage("User must have at least one role.");
        return false;
      }

      return newRoles;
    },
  }).then((result) => (result.isConfirmed ? result.value : null));
}
