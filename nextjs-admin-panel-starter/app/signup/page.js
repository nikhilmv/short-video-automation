"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation"; 
import FormField from "@/components/FormField";
import axios from "axios";

export default function SignupPage() { 
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [gender, setGender] = useState("Male");
  
 
  const handleSubmit = async (e)=> {
        e.preventDefault();
           setError("");
        
        setSubmitting(true);

        const response = await axios.post("http://localhost:5000/api/admin/register",{
            name,
            email,
            password,
            gender,
            dob,
            role
        },{
            withCredentials:true
        });
        if (response.data.success) {
            toast.success("user registered successfully!!");
            setTimeout(() => {
                router.push("./login");
            }, 500);
        } else {
                toast.error("user registeration failed!!");
                setError("user registeration failed!!");
        }
     
        
    }

  return (
    <div className="page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Create an account</h1>
        <p className="auth-subtitle">Get started with your admin panel.</p>

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
        <FormField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn-primary btn-block" disabled={submitting}>
          {submitting ? "Creating account..." : "Sign up"}
        </button>

        <p className="help-text">
          Already have an account?{" "}
          <Link href="/login" className="link">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}
