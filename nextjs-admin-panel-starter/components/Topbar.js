
"use client";

import { useDispatch, useSelector } from "react-redux";
import { useRouter } from "next/navigation";
import { logoutUser } from "@/app/store/authSlice";

export default function Topbar() {
  const { user, logoutLoading } = useSelector(
    (state) => state.auth
  );

  const dispatch = useDispatch();
  const router = useRouter();

  async function handleLogout() {
    try {
      await dispatch(logoutUser()).unwrap();
      router.replace("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  return (
    <header className="topbar">
      <span className="text-sm text-gray-500">
        Welcome, {user?.name}
      </span>

      <button
        className="btn-secondary"
        onClick={handleLogout}
        disabled={logoutLoading}
      >
        {logoutLoading ? "Logging out..." : "Log out"}
      </button>
    </header>
  );
}
