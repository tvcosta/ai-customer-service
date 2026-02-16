import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Customer Service Admin",
  description: "Admin dashboard for AI Customer Service system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
