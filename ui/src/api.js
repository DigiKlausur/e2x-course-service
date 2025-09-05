import { getCookie, urlJoin } from "./utils.js";

const baseSettings = {
  credentials: "same-origin",
  headers: {
    "X-CSRFToken": getCookie("_xsrf"),
  },
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json();
    const error = new Error(errorData.message || `HTTP ${response.status}`);
    error.response = { status: response.status, data: errorData };
    throw error;
  }
  return response.json();
};

const requests = {
  get: async (url, params = undefined) => {
    const settings = {
      ...baseSettings,
      method: "GET",
    };
    if (params !== undefined) {
      url += "?" + new URLSearchParams(params).toString();
    }
    const response = await fetch(url, settings);
    return handleResponse(response);
  },
  post: async (url, data) => {
    const settings = {
      ...baseSettings,
      method: "POST",
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response);
  },
  put: async (url, data) => {
    const settings = {
      ...baseSettings,
      method: "PUT",
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response);
  },
  del: async (url, data) => {
    const settings = {
      ...baseSettings,
      method: "DELETE",
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response);
  },
};

const courseAPI = {
  list: async () => {
    return requests.get(urlJoin(window.APP_CONFIG.api_url, "courses"));
  },
  members: {
    list: async (course_id, semester) => {
      return requests.get(
        urlJoin(window.APP_CONFIG.api_url, "course_members"),
        {
          course_id: course_id,
          semester: semester,
        },
      );
    },
    update: async (course_id, semester, members, add_to_hub = false) => {
      return requests.put(
        urlJoin(window.APP_CONFIG.api_url, "course_members"),
        {
          course_id: course_id,
          semester: semester,
          members: members,
          add_to_hub: add_to_hub,
        },
      );
    },
    delete: async (course_id, semester, members) => {
      return requests.del(
        urlJoin(window.APP_CONFIG.api_url, "course_members"),
        {
          course_id: course_id,
          semester: semester,
          members: members,
        },
      );
    },
  },
};

export const API = {
  courses: courseAPI,
};
