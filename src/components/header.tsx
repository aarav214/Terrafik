"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Search } from "lucide-react";

import { Logo } from "@/components/logo";
import { cn } from "@/lib/utils";

type PhotonFeature = {
  properties: Record<string, unknown>;
  geometry: { coordinates: [number, number] };
};

function getPlaceLabel(feature: PhotonFeature) {
  return (
    feature.properties.name ||
    feature.properties.osm_value ||
    feature.properties.city ||
    feature.properties.country ||
    "Search result"
  ) as string;
}

export function Header({ className }: { className?: string }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<PhotonFeature[]>([]);
  const [open, setOpen] = useState(false);
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch(
          `/api/search?q=${encodeURIComponent(query)}&limit=6`,
        );
        const json = await response.json();
        setSuggestions(json.features || []);
        setOpen(true);
      } catch (error) {
        console.error("Search suggestions failed:", error);
        setSuggestions([]);
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handleDocumentClick = (event: MouseEvent) => {
      if (!listRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    window.addEventListener("mousedown", handleDocumentClick);
    return () => window.removeEventListener("mousedown", handleDocumentClick);
  }, []);

  const submitSearch = (value: string, feature?: PhotonFeature) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    window.dispatchEvent(
      new CustomEvent("map-search", {
        detail: feature
          ? { query: trimmed, feature }
          : { query: trimmed },
      }),
    );
    setQuery(trimmed);
    setOpen(false);
  };

  return (
    <header
      className={cn(
        "bg-background/85 supports-backdrop-filter:bg-background/70 sticky top-0 z-50 h-14 w-full backdrop-blur",
        className,
      )}
    >
      <nav className="container flex size-full items-center gap-2">
        <Logo className="shrink-0" />
        <div className="ml-auto hidden sm:block">
          <div className="relative" ref={listRef}>
            <form
              onSubmit={(event: FormEvent<HTMLFormElement>) => {
                event.preventDefault();
                submitSearch(query);
              }}
              className="flex items-center gap-2 rounded-2xl border border-slate-300/30 bg-slate-100/90 px-3 py-2 shadow-sm backdrop-blur dark:border-slate-700/50 dark:bg-slate-950/80"
            >
              <Search className="size-4 text-slate-600 dark:text-slate-300" />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setOpen(true);
                }}
                placeholder="Search address or place"
                className="min-w-0 flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-500 dark:text-slate-100 dark:placeholder:text-slate-400"
              />
              <button
                type="submit"
                className="rounded-full bg-slate-200 px-3 py-1 text-sm font-medium text-slate-900 transition hover:bg-slate-300 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
              >
                Search
              </button>
            </form>

            {open && suggestions.length > 0 && (
              <div className="absolute right-0 top-full z-50 mt-2 w-md max-w-full overflow-hidden rounded-3xl border border-slate-200/70 bg-white/95 shadow-xl shadow-slate-900/10 backdrop-blur dark:border-slate-700/70 dark:bg-slate-950/95">
                <ul className="divide-y divide-slate-200/70 dark:divide-slate-700/70">
                  {suggestions.map((feature, index) => (
                    <li key={`${feature.geometry.coordinates[0]}-${feature.geometry.coordinates[1]}-${index}`}>
                      <button
                        type="button"
                        onClick={() => submitSearch(getPlaceLabel(feature), feature)}
                        className="w-full px-4 py-3 text-left text-sm text-slate-900 transition hover:bg-slate-100 dark:text-slate-100 dark:hover:bg-slate-800"
                      >
                        {getPlaceLabel(feature)}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
