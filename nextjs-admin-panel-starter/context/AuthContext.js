"use client";

import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

const USERS_KEY = "admin_panel_users";
const SESSION_KEY = "admin_panel_session";

// Seed one demo account so login works out of the box.
function seedUsers() {
  const existing = localStorage.getItem(USERS_KEY);
  if (!existing) {
    const seed = [
      {
        id: "1",
        name: "Demo Admin",
        email: "admin@example.com",
        password: "password123",
        role: "Admin",
        status: "Active",
      },
    ];
    localStorage.setItem(USERS_KEY, JSON.stringify(seed));
  }
}

function getUsers() {
  return JSON.parse(localStorage.getItem(USERS_KEY) || "[]");
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    seedUsers();
    const session = localStorage.getItem(SESSION_KEY);
    if (session) setUser(JSON.parse(session));
    setLoading(false);
  }, []);

  function login(email, password) {
    const users = getUsers();
    const match = users.find(
      (u) => u.email === email && u.password === password
    );
    if (!match) {
      return { ok: false, error: "Invalid email or password." };
    }
    const session = { id: match.id, name: match.name, email: match.email, role: match.role };
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    setUser(session);
    return { ok: true };
  }

  function signup(name, email, password) {
    const users = getUsers();
    if (users.some((u) => u.email === email)) {
      return { ok: false, error: "An account with this email already exists." };
    }
    const newUser = {
      id: String(Date.now()),
      name,
      email,
      password,
      role: "Member",
      status: "Active",
    };
    users.push(newUser);
    saveUsers(users);

    const session = { id: newUser.id, name: newUser.name, email: newUser.email, role: newUser.role };
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    setUser(session);
    return { ok: true };
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
    setUser(null);
  }

  function addUser(newUser) {
    const users = getUsers();
    if (users.some((u) => u.email === newUser.email)) {
      return { ok: false, error: "A user with this email already exists." };
    }
    const record = {
      id: String(Date.now()),
      password: "changeme123",
      status: "Active",
      ...newUser,
    };
    users.push(record);
    saveUsers(users);
    return { ok: true, user: record };
  }

  function listUsers() {
    return getUsers();
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, addUser, listUsers }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
