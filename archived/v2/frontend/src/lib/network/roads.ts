import { RoadElements, Intersection } from "../types";
import { CustomPopup } from "../popup";
import type { Map, Polyline, Marker, LatLngExpression, LeafletMouseEvent } from "leaflet";
import { getLeaflet } from "../leaflet_map";

const ROAD_STYLES: Record<string, { color: string; weight: number; opacity: number; zIndex: number }> = {
  motorway: { color: "#d73027", weight: 5, opacity: 1, zIndex: 100 },
  motorway_link: { color: "#d73027", weight: 5, opacity: 1, zIndex: 100 },
  trunk: { color: "#fc8d59", weight: 5, opacity: 1, zIndex: 90 },
  trunk_link: { color: "#fc8d59", weight: 5, opacity: 1, zIndex: 90 },
  primary: { color: "#fee090", weight: 5, opacity: 1, zIndex: 80 },
  primary_link: { color: "#fee090", weight: 5, opacity: 1, zIndex: 80 },
  secondary: { color: "#91bfdb", weight: 5, opacity: 1, zIndex: 70 },
  secondary_link: { color: "#91bfdb", weight: 5, opacity: 1, zIndex: 70 },
  tertiary: { color: "#4575b4", weight: 5, opacity: 1, zIndex: 60 },
  tertiary_link: { color: "#4575b4", weight: 5, opacity: 1, zIndex: 60 },
  residential: { color: "#999999", weight: 5, opacity: 0.9, zIndex: 50 },
  unclassified: { color: "#666666", weight: 5, opacity: 0.9, zIndex: 45 },
  living_street: { color: "#cccccc", weight: 4, opacity: 0.8, zIndex: 40 },
};

const DEFAULT_STYLE = {
  color: "#999999",
  weight: 2,
  opacity: 0.5,
  zIndex: 30,
};

export class RenderRoads {
  private map: Map;
  private polylines: Polyline[] = [];
  private intersection_markers: Marker[] = [];
  private current_popup: CustomPopup | null = null;
  private roads_data: RoadElements[] = [];
  private is_monochrome: boolean = false;

  constructor(map: Map) {
    this.map = map;
  }

  draw_roads(roads: RoadElements[]) {
    this.roads_data = roads;
    this.clear_roads();

    roads.forEach((road) => {
      const highway_type = road.tags?.highway;

      if (highway_type && road.geometry && road.geometry.length > 0) {
        const style = ROAD_STYLES[highway_type] || DEFAULT_STYLE;
        const color = this.is_monochrome ? "#666666" : style.color;

        const path: LatLngExpression[] = road.geometry.map((point) => [point.lat, point.lon]);

        const L = getLeaflet();
        if (!L) return;

        const polyline = L.polyline(path, {
          color: color,
          opacity: style.opacity,
          weight: style.weight,
        }).addTo(this.map);

        polyline.on("click", (e: LeafletMouseEvent) => {
          if (this.current_popup) {
            this.current_popup.remove();
          }

          const roadName = road.tags?.name || "Unnamed Road";
          const roadType = highway_type;
          const roadId = road.id;

          const content = `
            <div style="line-height: 1.5;">
              <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #000;">${roadName}</div>
              <div style="font-size: 12px; color: #666;">Type: ${roadType}</div>
              <div style="font-size: 12px; color: #666;">ID: ${roadId}</div>
            </div>
          `;

          this.current_popup = new CustomPopup(e.latlng, content);
          this.current_popup.setMap(this.map);
          this.current_popup.show();
        });

        this.polylines.push(polyline);
      }
    });
  }

  draw_intersections(intersections: Intersection[]) {
    this.clear_intersections();

    intersections.forEach((node) => {
      const L = getLeaflet();
      if (!L) return;

      const marker = L.marker([node.lat, node.lon], {
        icon: L.divIcon({
          className: "intersection-marker",
          html: '<div style="width: 14px; height: 14px; border-radius: 50%; background-color: #90EE90; border: 2px solid #000000;"></div>',
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        }),
      }).addTo(this.map);

      marker.on("click", () => {
        if (this.current_popup) {
          this.current_popup.remove();
        }

        const content = `
          <div style="line-height: 1.5;">
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #000;">Intersection</div>
            <div style="font-size: 12px; color: #666;">Node ID: ${node.id}</div>
          </div>
        `;

        this.current_popup = new CustomPopup([node.lat, node.lon], content);
        this.current_popup.setMap(this.map);
        this.current_popup.show();
      });

      this.intersection_markers.push(marker);
    });
  }

  toggle_monochrome() {
    this.is_monochrome = !this.is_monochrome;
    if (this.roads_data.length > 0) {
      this.draw_roads(this.roads_data);
    }
  }

  clear_intersections() {
    this.intersection_markers.forEach((marker) => this.map.removeLayer(marker));
    this.intersection_markers = [];
  }

  clear_roads() {
    this.polylines.forEach((polyline) => this.map.removeLayer(polyline));
    this.polylines = [];

    if (this.current_popup) {
      this.current_popup.remove();
      this.current_popup = null;
    }
  }

  clear_all() {
    this.clear_roads();
    this.clear_intersections();
  }
}
