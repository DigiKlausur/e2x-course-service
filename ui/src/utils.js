export const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    for (let cookie of document.cookie.split(";")) {
      if (cookie.trim().startsWith(`${name}=`)) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

export const urlJoin = (...parts) => {
  parts = parts.map((part, index) => {
    if (index) {
      part = part.replace(/^\//, "");
    }
    if (index !== parts.length - 1) {
      part = part.replace(/\/$/, "");
    }
    return part;
  });
  return parts.join("/");
};
