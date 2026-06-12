import { BarChart3, History, UploadCloud } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: BarChart3 },
  { to: "/upload", label: "Upload", icon: UploadCloud },
  { to: "/history", label: "History", icon: History }
];

export default function Navbar() {
  return (
    <header className="border-b border-bank-line bg-white">
      <nav className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="text-lg font-semibold text-bank-ink">
          BankDoc Verify
        </NavLink>
        <div className="flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex h-10 items-center gap-2 rounded-md px-3 text-sm font-medium ${
                  isActive ? "bg-bank-pale text-bank-blue" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  );
}
