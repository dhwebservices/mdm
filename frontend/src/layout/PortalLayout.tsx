import {
  Bell,
  ClipboardList,
  FileArchive,
  Gauge,
  Laptop,
  ListChecks,
  Package,
  ScrollText,
  Settings,
  ShieldCheck,
  Terminal,
  Users
} from "lucide-react";
import type { ReactNode } from "react";

const navItems = [
  { label: "Dashboard", icon: Gauge },
  { label: "Devices", icon: Laptop },
  { label: "Users", icon: Users },
  { label: "Policies", icon: ShieldCheck },
  { label: "Applications", icon: Package },
  { label: "Scripts", icon: Terminal },
  { label: "Compliance", icon: ListChecks },
  { label: "Assets", icon: FileArchive },
  { label: "Support", icon: ClipboardList },
  { label: "Audit Logs", icon: ScrollText },
  { label: "Settings", icon: Settings }
];

export function PortalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-surface">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white lg:block">
        <div className="border-b border-line px-5 py-5">
          <div className="text-base font-bold text-ink">DH MDM</div>
          <div className="text-xs text-slate-500">DH Website Services</div>
        </div>
        <nav className="space-y-1 px-3 py-4" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = item.label === "Dashboard";
            return (
              <button
                key={item.label}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm ${
                  active ? "bg-teal-50 text-teal-800" : "text-slate-700 hover:bg-slate-100"
                }`}
                type="button"
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-white/90 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-5">
            <div>
              <h1 className="text-lg font-semibold text-ink">Dashboard</h1>
              <p className="text-xs text-slate-500">Company-owned Apple fleet</p>
            </div>
            <button className="rounded-md p-2 text-slate-600 hover:bg-slate-100" type="button" aria-label="Notifications">
              <Bell className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </header>
        <div className="px-5 py-6">{children}</div>
      </main>
    </div>
  );
}
