import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEXUS-OSINT | 3D Link Analysis Platform",
  description: "AI-Native OSINT & 3D Link Analysis Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-nexus-900 text-gray-200 antialiased">
        {children}
      </body>
    </html>
  );
}
