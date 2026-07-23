import { useEffect, useRef, useState } from "react";
import foodPlaces from "./data/foodPlaces.js";

const GOOGLE_MAPS_API_KEY = import.meta.env.GOOGLE_MAPS_API_KEY;
const GOOGLE_MAPS_MAP_ID = import.meta.env.GOOGLE_MAPS_MAP_ID;

const SINGAPORE_CENTER = { lat: 1.3521, lng: 103.8198 };

const MapComponent = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [mapsLoaded, setMapsLoaded] = useState(false);

  useEffect(() => {
    if (window.google?.maps) {
      setMapsLoaded(true);
      return;
    }

    if (window.__googleMapsLoading) return;
    window.__googleMapsLoading = true;

    window.initMap = () => {
      window.__googleMapsLoaded = true;
      setMapsLoaded(true);
    };

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=marker&loading=async&callback=initMap`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
  }, []);

  useEffect(() => {
    if (!mapsLoaded || !mapRef.current || mapInstanceRef.current) return;

    const map = new window.google.maps.Map(mapRef.current, {
      zoom: 12,
      center: SINGAPORE_CENTER,
      mapTypeId: "roadmap",
      mapId: GOOGLE_MAPS_MAP_ID,
    });

    mapInstanceRef.current = map;

    foodPlaces.forEach((place) => {
      const marker = new window.google.maps.marker.AdvancedMarkerElement({
        map,
        position: { lat: place.lat, lng: place.lng },
        title: place.name,
      });

      const infoWindow = new window.google.maps.InfoWindow({
        content: `<div><strong>${place.name}</strong><br>${place.cuisine.join(", ")}</div>`,
      });

      marker.addListener("gmp-click", () => infoWindow.open(map, marker));
    });
  }, [mapsLoaded]);

  return (
    <div ref={mapRef} style={{ width: "100%", height: "calc(100vh - 80px)" }} />
  );
};

export default MapComponent;
