import { Coordinates, EarthquakeElements } from "../types";
import type { Map } from "leaflet";

const PYTHON_API = "http://localhost:8000";

export class RenderEarthquakes {
  private map: Map;

  constructor(map: Map) {
    this.map = map;
  }

  async get_earthquakes(coords: Coordinates): Promise<EarthquakeElements | null> {
    try {
      const response = await fetch(`${PYTHON_API}/api/earthquakes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(coords),
      });

      if (response.status === 404) {
        const errorData = await response.json().catch(() => ({ detail: "No earthquakes found" }));
        throw new Error(errorData.detail || "No earthquakes found");
      }

      if (!response.ok) {
        throw new Error("Failed to fetch earthquakes from API");
      }

      const earthquake_data = await response.json();

      if (!earthquake_data) {
        return null;
      }

      return earthquake_data;
    } catch (error) {
      throw error;
    }
  }
}
