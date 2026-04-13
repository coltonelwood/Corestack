import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ABF — Autonomous Business Factory",
  description: "Autonomous business operations platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
