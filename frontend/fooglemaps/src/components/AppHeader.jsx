import { useSidebar } from "../context/SidebarContext";
import UserMenu from "./UserMenu";

export default function AppHeader() {
  const { toggle, isMobile } = useSidebar();

  return (
    <header className="fixed top-0 left-0 right-0 h-header bg-header border-b border-border flex items-center px-4 gap-3 z-[100]">
      <div className="flex items-center gap-3">
        <button
          className="flex items-center justify-center w-9 h-9 rounded-sm text-content-secondary hover:bg-surface-tertiary transition-colors duration-200"
          onClick={toggle}
          aria-label={isMobile ? "Open menu" : "Toggle sidebar"}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <span className="text-lg font-bold text-primary whitespace-nowrap">Fooglemaps</span>
      </div>
      <div className="flex-1 flex justify-center max-w-[480px] mx-auto max-lg:max-w-none max-lg:mx-0 max-sm:hidden">
        <div className="relative w-full">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-content-muted pointer-events-none" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search food places..."
            className="w-full h-[38px] pl-9 pr-3 border border-border rounded-md bg-surface-secondary text-sm outline-none focus:border-primary focus:bg-surface focus:ring-[3px] focus:ring-primary/10 transition-[border-color,box-shadow] duration-200"
          />
        </div>
      </div>
      <div className="flex items-center">
        <UserMenu />
      </div>
    </header>
  );
}
