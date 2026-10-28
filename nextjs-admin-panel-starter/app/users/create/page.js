"use client";

import { useState } from "react";
import { useRouter } from "next/navigation"; 
import FormField from "@/components/FormField";
import axios from "axios";

export default function CreateUserPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("Member");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const response = await axios.post("http://localhost:5000/api/admin/users", {
        name,
        email,
        role
      }, {
        withCredentials: true
      });
      if (response.data.success) {
        router.push("/users");
      } else {
        setError(response.data.message || "Failed to create user");
      }
    } catch (err) {
      setError(err.response?.data?.message || "Failed to create user");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Create user</h1>
      </div>

      <form className="card max-w-md" onSubmit={handleSubmit}>
        <FormField
          label="Full name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <FormField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <div className="field">
          <label className="label">Role</label>
          <select
            className="input"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="Member">Member</option>
            <option value="Admin">Admin</option>
          </select>
        </div>

        {error && <p className="error-text">{error}</p>}

        <div className="flex gap-3 mt-2">
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Creating..." : "Create user"}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => router.push("/users")}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
