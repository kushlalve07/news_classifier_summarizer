import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const registerUser = (username, password) =>
    axios.post(`${BASE}/auth/register`, { username, password });

export const loginUser = (username, password) =>
    axios.post(`${BASE}/auth/login`, { username, password });

export const savePreferences = (user_id, topics, city) =>
    axios.post(`${BASE}/preferences/save`, { user_id, topics, city });

export const getPreferences = (user_id) =>
    axios.get(`${BASE}/preferences/${user_id}`);

export const getFeed = (user_id) =>
    axios.post(`${BASE}/feed`, { user_id });