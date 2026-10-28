import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import StoreProvider from "./StoreProvider";

export const metadata = {
  title: "Admin Panel",
  description: "Next.js admin panel starter",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <StoreProvider>{children}</StoreProvider>
      </body>
    </html>
  );
}
