import React, { useEffect, useRef, useState } from "react";

const MapComponent = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [mapsLoaded, setMapsLoaded] = useState(false);

  // Sample food places in Singapore (name, lat, lng, cuisine)
  const foodPlaces = [
    {
      name: "Maxwell Food Centre",
      lat: 1.2819,
      lng: 103.8307,
      cuisine: ["Hawker", "Chinese"],
    },
    {
      name: "Lau Pa Sat",
      lat: 1.276,
      lng: 103.8512,
      cuisine: ["Hawker", "Satay"],
    },
    {
      name: "Chinatown Complex Food Centre",
      lat: 1.2803,
      lng: 103.8424,
      cuisine: ["Hawker", "Chinese"],
    },
    {
      name: "Tekka Centre",
      lat: 1.308,
      lng: 103.8495,
      cuisine: ["Hawker", "Indian"],
    },
    {
      name: "Old Airport Road Food Centre",
      lat: 1.3205,
      lng: 103.9088,
      cuisine: ["Hawker", "Various"],
    },
  ];

  const GOOGLE_MAPS_API_KEY = import.meta.env.GOOGLE_MAPS_API_KEY;
  const GOOGLE_MAPS_MAP_ID = import.meta.env.GOOGLE_MAPS_MAP_ID;

  // Load Google Maps API with Marker library dynamically
  useEffect(() => {
    // If Google Maps is already loaded, just set ready
    if (window.google && window.google.maps) {
      setMapsLoaded(true);
      return;
    }

    // Prevent duplicate loading attempts
    if (window.__googleMapsLoading) {
      return;
    }

    // Mark that we've started loading
    window.__googleMapsLoading = true;

    // DEFINE THE CALLBACK FIRST before adding the script to DOM
    // This prevents a race condition where the script might start loading
    // before we set the callback
    window.initMap = () => {
      // Mark as loaded on window for fast checking
      window.__googleMapsLoaded = true;
      // Update React state
      setMapsLoaded(true);
    };

    // Build the script URL
    let scriptSrc = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=marker&loading=async&callback=initMap`;

    // Create script element
    const script = document.createElement("script");
    script.src = scriptSrc;
    script.async = true;
    script.defer = true;

    // Add to document head
    document.head.appendChild(script);

    // CRITICAL: Do NOT clean up the callback or loading flag in cleanup
    // This prevents "initMap is not a function" errors when the script finishes
    // loading after the component unmounts (e.g., in React StrictMode)
    return () => {
      // Intentionally empty - we do NOT clean up our globals
      // because the script might still be loading and need to call the callback
    };
  }, []); // Empty deps = run once on mount

  // Initialize map when we have the ref and maps are loaded
  useEffect(() => {
    if (mapsLoaded && mapRef.current && !mapInstanceRef.current) {
      // Create the map instance
      const map = new window.google.maps.Map(mapRef.current, {
        zoom: 12,
        center: { lat: 1.3521, lng: 103.8198 },
        mapTypeId: "roadmap",
        mapId: GOOGLE_MAPS_MAP_ID,
      });

      // Store the map instance to prevent re-creation
      mapInstanceRef.current = map;

      // Add markers for each food place
      foodPlaces.forEach((place) => {
        // Create Advanced Marker (works best with Map ID)
        const marker = new window.google.maps.marker.AdvancedMarkerElement({
          map,
          position: { lat: place.lat, lng: place.lng },
          title: place.name,
        });

        // Create info window for the marker
        const infoWindow = new window.google.maps.InfoWindow({
          content: `<div><strong>${place.name}</strong><br>${place.cuisine.join(
            ", ",
          )}</div>`,
        });

        // Add click listener - use gmp-click for AdvancedMarkerElement
        marker.addListener("gmp-click", () => {
          infoWindow.open(map, marker);
        });
      });
    }
  }, [mapsLoaded]); // Re-run when mapsLoaded changes

  return (
    <div>
      <div
        ref={mapRef}
        style={{ width: "100%", height: "calc(100vh - 80px)" }}
      />
    </div>
  );
};

export default MapComponent;
