import type { Map } from "leaflet";

export interface MapProps {
  map: Map | null;
}

export interface LegendProps {
  show: boolean;
}

export interface Coordinates {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface RoadElements {
  type: string;
  id: number;
  nodes?: number[];
  geometry?: Array<{ lat: number; lon: number }>;
  tags?: {
    highway?: string;
    name?: string;
    [key: string]: unknown;
  };
}

export interface Roads {
  elements: RoadElements[];
}

export interface Intersection {
  type: string;
  id: number;
  lat: number;
  lon: number;
}

export interface Intersections {
  elements: Intersection[];
}

export interface Bridge {
  lat: number;
  lng: number;
  location: string;
  id: string;
}

export interface EarthquakeElements {
  id: string;
  properties: {
    mag: number;
    place: string;
    time: number;
    updated: number;
    url: string;
    detail: string;
    title: string;
  };
  geometry: {
    coordinates: [number, number, number];
  };
}

export interface Earthquake {
  features: EarthquakeElements[];
}

export interface ShakemapData {
  id: string;
  actual_magnitude: number;
  location: string;
  time: number;
  depth: number;
  latitude: number;
  longitude: number;
  vs30: number;
  ground_motions: {
    PGA?: GroundMotion;
    PGV?: GroundMotion;
    MMI?: GroundMotion;
    SA03?: GroundMotion;
    SA10?: GroundMotion;
  };
}

interface GroundMotion {
  units: string;
  max: number;
  max_grid: number;
  bias: number;
}
