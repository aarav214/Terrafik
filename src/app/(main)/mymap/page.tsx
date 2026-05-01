"use client";

import { useEffect, useRef, useState } from "react";
import { Map, MapControls, type MapRef } from "@/registry/map";
import MapLibreGL from "maplibre-gl";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const DEFAULT_START: [number, number] = [-74.006, 40.7128];

type Location = {
  name: string;
  coords: [number, number];
};

type UIMode = "idle" | "preview" | "routing";

export default function MyMap() {
  const mapRef = useRef<MapRef | null>(null);
  const searchMarkerRef = useRef<MapLibreGL.Marker | null>(null);
  const [uiMode, setUiMode] = useState<UIMode>("idle");
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [routeType, setRouteType] = useState<"safest" | "fastest" | null>(null);
  const [routeReasoning, setRouteReasoning] = useState<string>("");

  const resetSelection = () => {
    setUiMode("idle");
    setSelectedLocation(null);
    setRouteType(null);
    setRouteReasoning("");

    if (searchMarkerRef.current) {
      searchMarkerRef.current.remove();
      searchMarkerRef.current = null;
    }

    const map = mapRef.current;
    if (map) {
      if (map.getLayer("route-line")) {
        map.removeLayer("route-line");
      }
      if (map.getSource("route-source")) {
        map.removeSource("route-source");
      }
    }
  };

  const beginRouting = (type: "safest" | "fastest") => {
    if (!selectedLocation) return;

    setRouteType(type);
    setUiMode("routing");
    setRouteReasoning(
      type === "safest"
        ? "Avoiding Central Ave due to 70% flood risk."
        : "Prioritizing fastest travel time along major roads."
    );
  };

  useEffect(() => {
    const handleSearch = async (event: CustomEvent) => {
      const { query, feature } = event.detail;
      if (!query || !mapRef.current) return;

      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
          query,
        )}&format=json`
      );
      const data = await res.json();
      if (!data.length) return;

      const place = data[0];
      const coords: [number, number] = [
        parseFloat(place.lon),
        parseFloat(place.lat),
      ];
      const name = (feature as any)?.properties?.name || query || "Selected location";

      mapRef.current.flyTo({
        center: coords,
        zoom: 14,
      });

      if (searchMarkerRef.current) {
        searchMarkerRef.current.remove();
      }
      searchMarkerRef.current = new MapLibreGL.Marker({ color: "#0ea5e9" })
        .setLngLat(coords)
        .addTo(mapRef.current);

      setSelectedLocation({ name, coords });
      setUiMode("preview");
    };

    window.addEventListener("map-search", handleSearch as EventListener);
    return () => window.removeEventListener("map-search", handleSearch as EventListener);
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const handleClick = (event: MapLibreGL.MapMouseEvent) => {
      const coords: [number, number] = [event.lngLat.lng, event.lngLat.lat];
      if (searchMarkerRef.current) {
        searchMarkerRef.current.remove();
      }
      searchMarkerRef.current = new MapLibreGL.Marker({ color: "#0ea5e9" })
        .setLngLat(coords)
        .addTo(map);

      setSelectedLocation({
        name: `Selected point (${coords[1].toFixed(4)}, ${coords[0].toFixed(4)})`,
        coords,
      });
      setUiMode("preview");
    };

    map.on("click", handleClick);
    return () => {
      map.off("click", handleClick);
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const removeRoute = () => {
      if (map.getLayer("route-line")) {
        map.removeLayer("route-line");
      }
      if (map.getSource("route-source")) {
        map.removeSource("route-source");
      }
    };

    if (uiMode === "routing" && routeType === "safest" && selectedLocation) {
      const origin = map.getCenter();
      const route = {
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: [
            [origin.lng, origin.lat],
            selectedLocation.coords,
          ],
        },
      } as const;

      if (map.getSource("route-source")) {
        const source = map.getSource("route-source") as MapLibreGL.GeoJSONSource;
        source.setData(route);
      } else {
        map.addSource("route-source", {
          type: "geojson",
          data: route,
        });
        map.addLayer({
          id: "route-line",
          type: "line",
          source: "route-source",
          layout: {
            "line-join": "round",
            "line-cap": "round",
          },
          paint: {
            "line-color": "#22c55e",
            "line-width": 5,
            "line-opacity": 0.85,
          },
        });
      }
    } else {
      removeRoute();
    }

    return removeRoute;
  }, [uiMode, routeType, selectedLocation]);

  return (
    <div className="h-screen w-full relative">
      <Map ref={mapRef} center={DEFAULT_START} zoom={11}>
        <MapControls />
      </Map>

      {uiMode === "preview" && selectedLocation && (
        <Card className="absolute bottom-8 left-1/2 z-20 w-[90%] max-w-sm -translate-x-1/2 animate-in slide-in-from-bottom">
          <CardHeader>
            <CardTitle>{selectedLocation.name}</CardTitle>
            <CardDescription>High Risk Area (Flood Zone)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Choose a route to analyze the safest or fastest path to this location.
            </p>
            <div className="flex flex-col gap-2">
              <Button className="w-full" onClick={() => beginRouting("safest")}>Safest Path</Button>
              <Button variant="secondary" className="w-full" onClick={() => beginRouting("fastest")}>Fastest Path</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {uiMode === "routing" && selectedLocation && (
        <div className="absolute top-4 left-4 z-20">
          <Card className="w-80 space-y-4 shadow-lg">
            <div className="flex items-center justify-between gap-4 px-4 pt-4">
              <div>
                <div className="text-sm font-semibold">Route to {selectedLocation.name}</div>
                <p className="text-xs text-muted-foreground">{routeType === "safest" ? "Safest" : "Fastest"} route active</p>
              </div>
              <Button variant="ghost" size="icon" onClick={resetSelection}>
                X
              </Button>
            </div>
            <CardContent className="pb-4">
              <p className="text-sm text-muted-foreground">{routeReasoning}</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}