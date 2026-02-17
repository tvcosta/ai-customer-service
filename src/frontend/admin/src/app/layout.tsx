import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/layout/error-boundary";

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
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
        <Toaster position="bottom-right" richColors closeButton />
      </body>
    </html>
  );
}
