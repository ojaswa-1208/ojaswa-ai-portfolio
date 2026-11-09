import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ojaswa Mahobiya | AI Engineer",
  description:
    "Ojaswa Mahobiya — AI/ML engineering student exploring AI engineering, LLMs, RAG systems and Agentic AI.",
  keywords: [
    "Ojaswa Mahobiya",
    "AI Engineer",
    "Agentic AI",
    "Machine Learning",
    "RAG",
    "Python",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}