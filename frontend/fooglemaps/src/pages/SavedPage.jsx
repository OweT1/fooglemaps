import PageContainer from "../components/PageContainer";
import foodPlaces from "../data/foodPlaces.js";

export default function SavedPage() {
  return (
    <PageContainer title="Saved Places" subtitle="Your bookmarked food spots">
      <div className="flex flex-col gap-2">
        {foodPlaces.map((place) => (
          <div key={place.name} className="flex items-center justify-between px-4 py-3.5 border border-border rounded-md hover:border-primary transition-colors duration-200">
            <div>
              <h3 className="text-[15px] font-semibold">{place.name}</h3>
              <div className="flex gap-1.5 mt-1.5">
                {place.cuisine.map((c) => (
                  <span key={c} className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-surface-tertiary text-content-secondary">{c}</span>
                ))}
              </div>
            </div>
            <button className="flex items-center justify-center w-9 h-9 rounded-full text-primary hover:bg-surface-tertiary transition-colors duration-200" aria-label={`Remove ${place.name}`}>
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
