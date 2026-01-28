import { Coordinates } from "../types";
import { CustomPopup } from "../popup";
import type { Map, Marker } from "leaflet";
import { getLeaflet } from "../leaflet_map";

const PYTHON_API = "http://localhost:8000";

interface BridgeData {
  LATITUDE: number;
  LONGITUDE: number;
  LOCATION_009?: string;
  name?: string;
  id: string | number;
}

export class RenderBridges {
  private map: Map;
  private markers: Marker[] = [];
  private bridges_data: BridgeData[] = [];
  private currentPopup: CustomPopup | null = null;

  constructor(map: Map) {
    this.map = map;
  }

  async draw_bridges(coords: Coordinates) {
    this.clear_bridges();

    try {
      const response = await fetch(`${PYTHON_API}/api/bridges`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(coords),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch bridges from Python API");
      }

      const bridges = await response.json();

      this.bridges_data = bridges;

      bridges.forEach((bridge: BridgeData) => {
        const L = getLeaflet();
        if (!L) return;

        const marker = L.marker([bridge.LATITUDE, bridge.LONGITUDE], {
          icon: L.divIcon({
            className: "bridge-marker",
            html: '<div style="width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 20px solid #964B00; border-top: 0; position: relative;"><div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 16px solid #000000; position: absolute; top: 4px; left: -8px;"></div></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 20],
          }),
        }).addTo(this.map);

        marker.on("click", () => {
          if (this.currentPopup) {
            this.currentPopup.remove();
          }

          const content = `
            <div style="line-height: 1.5;">
              <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #000;">${bridge.LOCATION_009 || bridge.name || "Bridge"}</div>
              <div style="font-size: 12px; color: #666;">ID: ${bridge.id}</div>
            </div>
          `;

          this.currentPopup = new CustomPopup([bridge.LATITUDE, bridge.LONGITUDE], content);
          this.currentPopup.setMap(this.map);
          this.currentPopup.show();
        });

        this.markers.push(marker);
      });
    } catch (error) {
      throw error;
    }
  }

  get_bridges_data() {
    return this.bridges_data;
  }

  clear_bridges() {
    this.markers.forEach((marker) => this.map.removeLayer(marker));
    this.markers = [];

    if (this.currentPopup) {
      this.currentPopup.remove();
      this.currentPopup = null;
    }
  }
}
