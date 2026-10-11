import { useEffect, useRef, useState } from "react";

import { SINGAPORE_CENTER } from "./constants/maps.js";
import config from "./config/config.js";

const [GOOGLE_MAPS_API_KEY, GOOGLE_MAPS_MAP_ID] = [
  config.GOOGLE_MAPS.API_KEY,
  config.GOOGLE_MAPS.MAP_ID,
];

const MapComponent = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const [mapsLoaded, setMapsLoaded] = useState(false);
  const [places, setPlaces] = useState([]);

  useEffect(() => {
    fetch("/api/places")
      .then((r) => r.json())
      .then((data) => {
        if (data.type === "FeatureCollection") {
          setPlaces(data.features);
        }
      })
      .catch(() => {});
  }, []);

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
  }, [mapsLoaded]);

  useEffect(() => {
    if (!mapsLoaded || !mapInstanceRef.current) return;

    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    const map = mapInstanceRef.current;

    places.forEach((feature) => {
      const [lng, lat] = feature.geometry.coordinates;
      const props = feature.properties;

      const marker = new window.google.maps.marker.AdvancedMarkerElement({
        map,
        position: { lat, lng },
        title: props.name,
      });

      const infoWindow = new window.google.maps.InfoWindow({
        content: `<div><strong>${props.name}</strong>${
          props.address ? `<br>${props.address}` : ""
        }${
          props.cuisine_tags?.length
            ? `<br>${props.cuisine_tags.join(", ")}`
            : ""
        }</div>`,
      });

      marker.addListener("gmp-click", () => infoWindow.open(map, marker));
      markersRef.current.push(marker);
    });
  }, [mapsLoaded, places]);

  return <div ref={mapRef} className="flex-1 min-h-0" />;
};

export default MapComponent;
