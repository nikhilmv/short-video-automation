"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation"; 
import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import { useSelector } from "react-redux";

export default function ProtectedShell({ children }) {
  const { user, loading } = useSelector((state) => state.auth);
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return <div className="page">Loading...</div>;
  }

  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
