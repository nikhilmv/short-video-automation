"use client";
 
import { useState, useEffect } from "react";
import axios from "axios";

export default function DashboardPage() { 
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/admin/users", {
          withCredentials: true,
        });
        if (response.data.success) {
          setUsers(response.data.users || []);
        }
      } catch (err) {
        console.error("Failed to fetch users", err);
      }
    };
    fetchUsers();
  }, []);

  const activeUsers = users.filter((u) => u.status === "Active").length;

  const stats = [
    { label: "Total users", value: users.length },
    { label: "Active users", value: activeUsers },
    { label: "Admins", value: users.filter((u) => u.role === "Admin").length },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="stat-card">
            <p className="stat-label">{stat.label}</p>
            <p className="stat-value">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
