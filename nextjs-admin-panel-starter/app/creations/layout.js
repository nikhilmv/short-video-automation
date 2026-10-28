import ProtectedShell from "@/components/ProtectedShell";

export const metadata = {
  title: "Creations",
};

export default function DocumentsLayout({ children }) {
  return <ProtectedShell>{children}</ProtectedShell>;
}
