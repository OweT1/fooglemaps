import { useState } from "react";

import PageContainer from "../components/PageContainer";
import { useCuisines } from "../context/CuisineContext";

export default function SearchPage() {
  const { cuisines, loading } = useCuisines();
  const [cuisine, setCuisine] = useState("");

  return (
    <PageContainer title="Search" subtitle="Find food places by name, cuisine, or location">
      <div className="max-w-[600px]">
        <div className="flex flex-col gap-3 mb-6">
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-content-muted" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input type="text" placeholder="Search by name, cuisine..." className="w-full h-[42px] pl-[38px] pr-3 border border-border rounded-md bg-surface-secondary text-sm outline-none focus:border-primary focus:bg-surface focus:ring-[3px] focus:ring-primary/10" />
          </div>
          <div className="flex gap-2">
            <select
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
              disabled={loading}
              className="flex-1 h-[38px] px-2.5 border border-border rounded-sm bg-surface text-[13px] outline-none disabled:opacity-60"
            >
              <option value="" disabled>Cuisine</option>
              {cuisines.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <select defaultValue="" className="flex-1 h-[38px] px-2.5 border border-border rounded-sm bg-surface text-[13px] outline-none">
              <option value="" disabled>Location</option>
              <option value="central">Central</option>
              <option value="east">East</option>
              <option value="west">West</option>
              <option value="north">North</option>
            </select>
          </div>
          <button className="h-10 px-5 rounded-sm bg-primary text-white font-semibold text-sm hover:bg-primary-hover transition-colors duration-200">Search</button>
        </div>
        <div>
          <p className="text-center py-12 px-5 text-content-muted text-sm">Enter a search term or browse the map to discover food places.</p>
        </div>
      </div>
    </PageContainer>
  );
}
