import { NavLink } from "react-router-dom";
import { useSidebar } from "../context/SidebarContext";

const NAV_ITEMS = [
  {
    to: "/",
    label: "Home",
    icon: <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />,
  },
  {
    to: "/maps",
    label: "Maps",
    icon: (
      <>
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
        <circle cx="12" cy="10" r="3" />
      </>
    ),
  },
  {
    to: "/feed",
    label: "Feed",
    icon: (
      <>
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </>
    ),
  },
  {
    to: "/search",
    label: "Search",
    icon: (
      <>
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </>
    ),
  },
  {
    to: "/saved",
    label: "Saved",
    icon: <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />,
  },
  {
    to: "/settings",
    label: "Settings",
    icon: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
      </>
    ),
  },
];

export default function NavSidebar() {
  const { collapsed, mobileOpen, closeMobile } = useSidebar();

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/30 z-[89]" onClick={closeMobile} />
      )}
      <nav
        className={`
          ${collapsed ? 'w-sidebar-sm' : 'w-sidebar'}
          max-lg:!w-sidebar
          flex-shrink-0 bg-sidebar border-r border-border py-3 px-2 overflow-y-auto
          flex flex-col gap-0.5
          max-lg:fixed max-lg:top-header max-lg:left-0 max-lg:bottom-footer max-lg:z-[90]
          max-lg:transition-transform max-lg:duration-200
          ${mobileOpen ? 'max-lg:translate-x-0' : 'max-lg:-translate-x-full'}
          transition-[width] duration-200
        `}
      >
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center ${collapsed ? 'justify-center px-0 py-2.5' : 'gap-3 px-3 py-2.5'} rounded-sm
               ${isActive ? 'bg-primary text-white' : 'text-content-secondary'}
               hover:bg-surface-tertiary hover:text-content
               transition-colors duration-200 whitespace-nowrap overflow-hidden`
            }
            onClick={closeMobile}
          >
            <span className="flex items-center justify-center flex-shrink-0 w-5 h-5">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                {item.icon}
              </svg>
            </span>
            {!collapsed && (
              <span className="text-sm font-medium opacity-100 transition-opacity duration-200">
                {item.label}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
