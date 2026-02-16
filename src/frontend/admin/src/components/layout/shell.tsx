import { Sidebar } from "./sidebar";
import { Header } from "./header";

interface ShellProps {
  title: string;
  children: React.ReactNode;
}

export function Shell({ title, children }: ShellProps) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
