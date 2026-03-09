import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SPRKTech magic",
  description: "Chat with your documents using RAG",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
