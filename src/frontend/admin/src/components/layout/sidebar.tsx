"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Database, MessageSquare, PlayCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Knowledge Bases",
    href: "/knowledge-bases",
    icon: Database,
  },
  {
    name: "Interactions",
    href: "/interactions",
    icon: MessageSquare,
  },
  {
    name: "Playground",
    href: "/playground",
    icon: PlayCircle,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col bg-gray-900 text-white">
      <div className="flex h-16 items-center border-b border-gray-800 px-6">
        <h1 className="text-xl font-bold">AI Customer Service</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
