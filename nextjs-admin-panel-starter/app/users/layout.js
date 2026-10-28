import ProtectedShell from "@/components/ProtectedShell";

export default function UsersLayout({ children }) {
  return <ProtectedShell>{children}</ProtectedShell>;
}
