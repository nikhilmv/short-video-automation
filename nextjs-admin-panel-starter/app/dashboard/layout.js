import ProtectedShell from "@/components/ProtectedShell";

export default function DashboardLayout({ children }) {
  return <ProtectedShell>{children}</ProtectedShell>;
}
