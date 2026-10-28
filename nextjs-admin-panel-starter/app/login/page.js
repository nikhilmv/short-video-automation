"use client";

import { useState } from "react";
import Link from "next/link"; 
import FormField from "@/components/FormField";
import { useDispatch } from "react-redux";
import { useRouter } from "next/navigation";
import axios from "axios";
import { setUser } from "../store/authSlice";

export default function LoginPage() {  
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  
    const dispatch = useDispatch();

    const router = useRouter();

  const handleSubmit = async (e) => {

        e.preventDefault();
        setError("");
        setSubmitting(true);
        try {

        const response = await axios.post("http://localhost:5000/api/admin/login",{
            email,
            password
        },{
            withCredentials:true,
        });
        if(response.data.success){
            dispatch(setUser(response.data.user));
            router.push("dashboard");
        } else {
            setError(response.data.message);
        }
        } catch (err) {
            setError(err.response?.data?.message || "Login failed");
            
        } finally{
            setSubmitting(false);
        }
            
        
    }

  return (
    <div className="page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Log in</h1>
        <p className="auth-subtitle">Use the demo account or your own.</p>

        <FormField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <FormField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn-primary btn-block" disabled={submitting}>
          {submitting ? "Logging in..." : "Log in"}
        </button>

        <p className="help-text">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="link">
            Sign up
          </Link>
        </p>
      </form>
    </div>
  );
}
