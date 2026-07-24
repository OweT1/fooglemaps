import PageContainer from "../components/PageContainer";

export default function HomePage() {
  return (
    <PageContainer title="Dashboard" subtitle="Welcome to Fooglemaps">
      <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-4 max-sm:grid-cols-1">
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-3">Quick Actions</h3>
          <div className="flex flex-col gap-2">
            <button className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-sm bg-surface-secondary text-sm font-medium hover:bg-surface-tertiary transition-colors duration-200" onClick={() => window.location.href = "/maps"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              Explore Map
            </button>
            <button className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-sm bg-surface-secondary text-sm font-medium hover:bg-surface-tertiary transition-colors duration-200" onClick={() => window.location.href = "/search"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Search Food
            </button>
            <button className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-sm bg-surface-secondary text-sm font-medium hover:bg-surface-tertiary transition-colors duration-200" onClick={() => window.location.href = "/saved"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
              </svg>
              View Saved
            </button>
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-3">Food Spots Loaded</h3>
          <p className="text-[32px] font-extrabold text-primary">5</p>
          <p className="mt-1 text-[13px] text-content-secondary">Featured locations across Singapore</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-3">Cuisines</h3>
          <div className="flex flex-wrap gap-2">
            <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">Hawker</span>
            <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">Chinese</span>
            <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">Indian</span>
            <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">Satay</span>
            <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">Various</span>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
