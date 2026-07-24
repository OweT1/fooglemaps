import PageContainer from "../components/PageContainer";
import foodPlaces from "../data/foodPlaces.js";

export default function SavedPage() {
  return (
    <PageContainer title="Saved Places" subtitle="Your bookmarked food spots">
      <div className="saved-places">
        {foodPlaces.map((place) => (
          <div key={place.name} className="place-card">
            <div className="place-card-info">
              <h3>{place.name}</h3>
              <div className="place-card-tags">
                {place.cuisine.map((c) => (
                  <span key={c} className="tag">{c}</span>
                ))}
              </div>
            </div>
            <button className="bookmark-btn active" aria-label={`Remove ${place.name}`}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </PageContainer>
  );
}
