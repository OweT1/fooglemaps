import PageContainer from "../components/PageContainer";

export default function SearchPage() {
  return (
    <PageContainer title="Search" subtitle="Find food places by name, cuisine, or location">
      <div className="search-page">
        <div className="search-form">
          <div className="search-input-wrapper">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input type="text" placeholder="Search by name, cuisine..." />
          </div>
          <div className="search-filters">
            <select defaultValue="">
              <option value="" disabled>Cuisine</option>
              <option value="hawker">Hawker</option>
              <option value="chinese">Chinese</option>
              <option value="indian">Indian</option>
              <option value="satay">Satay</option>
            </select>
            <select defaultValue="">
              <option value="" disabled>Location</option>
              <option value="central">Central</option>
              <option value="east">East</option>
              <option value="west">West</option>
              <option value="north">North</option>
            </select>
          </div>
          <button className="search-submit">Search</button>
        </div>
        <div className="search-results">
          <p className="empty-state">Enter a search term or browse the map to discover food places.</p>
        </div>
      </div>
    </PageContainer>
  );
}
