"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/users", label: "Users" },
  { href: "/creations", label: "Creations" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">Admin Panel</div>
      <nav className="sidebar-nav">
        {links.map((link) => {
          const active =
            pathname === link.href || pathname.startsWith(link.href + "/");
          return (
            <Link
              key={link.href}
              href={link.href}
              className={active ? "sidebar-link-active" : "sidebar-link"}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
