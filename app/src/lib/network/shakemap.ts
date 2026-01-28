import { EarthquakeElements, ShakemapData } from "../types";

const PYTHON_API = "http://localhost:8000";

export const fetch_shakemap = async (earthquake: EarthquakeElements): Promise<ShakemapData | null> => {
  const event_id = earthquake.id;

  try {
    const response = await fetch(`${PYTHON_API}/api/shakemap?event_id=${event_id}`);

    if (!response.ok) {
      return null;
    }

    const shakemap_data = await response.json();
    const ground_motions = shakemap_data.output?.ground_motions || {};

    return {
      id: event_id,
      actual_magnitude: earthquake.properties.mag,
      location: earthquake.properties.place,
      time: earthquake.properties.time,
      depth: earthquake.geometry.coordinates[2],
      latitude: earthquake.geometry.coordinates[1],
      longitude: earthquake.geometry.coordinates[0],
      vs30: parseFloat(shakemap_data.processing?.site_response?.vs30default || "0"),
      ground_motions: {
        PGA: ground_motions.PGA
          ? {
              units: ground_motions.PGA.units,
              max: ground_motions.PGA.max,
              max_grid: ground_motions.PGA.max_grid,
              bias: ground_motions.PGA.bias,
            }
          : undefined,
        PGV: ground_motions.PGV
          ? {
              units: ground_motions.PGV.units,
              max: ground_motions.PGV.max,
              max_grid: ground_motions.PGV.max_grid,
              bias: ground_motions.PGV.bias,
            }
          : undefined,
        MMI: ground_motions.MMI
          ? {
              units: ground_motions.MMI.units,
              max: ground_motions.MMI.max,
              max_grid: ground_motions.MMI.max_grid,
              bias: ground_motions.MMI.bias,
            }
          : undefined,
        SA03: ground_motions["SA(0.3)"]
          ? {
              units: ground_motions["SA(0.3)"].units,
              max: ground_motions["SA(0.3)"].max,
              max_grid: ground_motions["SA(0.3)"].max_grid,
              bias: ground_motions["SA(0.3)"].bias,
            }
          : undefined,
        SA10: ground_motions["SA(1.0)"]
          ? {
              units: ground_motions["SA(1.0)"].units,
              max: ground_motions["SA(1.0)"].max,
              max_grid: ground_motions["SA(1.0)"].max_grid,
              bias: ground_motions["SA(1.0)"].bias,
            }
          : undefined,
      },
    };
  } catch (error) {
    return null;
  }
};
