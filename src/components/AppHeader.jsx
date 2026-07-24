import { useSidebar } from "../context/SidebarContext";

export default function AppHeader() {
  const { toggle, isMobile } = useSidebar();

  return (
    <header className="app-header">
      <div className="app-header-left">
        <button
          className="sidebar-toggle"
          onClick={toggle}
          aria-label={isMobile ? "Open menu" : "Toggle sidebar"}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <span className="app-logo">Fooglemaps</span>
      </div>
      <div className="app-header-center">
        <div className="search-bar">
          <svg className="search-bar-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input type="text" placeholder="Search food places..." />
        </div>
      </div>
      <div className="app-header-right">
        <button className="user-avatar" aria-label="User menu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
      </div>
    </header>
  );
}
