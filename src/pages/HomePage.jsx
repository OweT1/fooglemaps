import PageContainer from "../components/PageContainer";
import { useSidebar } from "../context/SidebarContext";

export default function HomePage() {
  const { isMobile } = useSidebar();

  return (
    <PageContainer title="Dashboard" subtitle="Welcome to Fooglemaps">
      <div className="home-grid">
        <div className="card">
          <h3>Quick Actions</h3>
          <div className="quick-actions">
            <button className="action-btn" onClick={() => window.location.href = "/maps"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              Explore Map
            </button>
            <button className="action-btn" onClick={() => window.location.href = "/search"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Search Food
            </button>
            <button className="action-btn" onClick={() => window.location.href = "/saved"}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
              </svg>
              View Saved
            </button>
          </div>
        </div>
        <div className="card">
          <h3>Food Spots Loaded</h3>
          <p className="stat-number">5</p>
          <p className="stat-label">Featured locations across Singapore</p>
        </div>
        <div className="card">
          <h3>Cuisines</h3>
          <div className="cuisine-tags">
            <span className="tag">Hawker</span>
            <span className="tag">Chinese</span>
            <span className="tag">Indian</span>
            <span className="tag">Satay</span>
            <span className="tag">Various</span>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
