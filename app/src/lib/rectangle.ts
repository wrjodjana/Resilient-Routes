import { Coordinates } from "./types";
import type { Map, Rectangle } from "leaflet";
import { getLeaflet } from "./leaflet_map";

export class RectangleManager {
  private map: Map;
  private draw_control: any = null;
  private current_rectangle: Rectangle | null = null;
  private editable_layer: any = null;
  private edit_control: any = null;
  private on_coordinates_change: (coords: Coordinates | null) => void;

  constructor(map: Map, on_coordinates_change: (coords: Coordinates | null) => void) {
    this.map = map;
    this.on_coordinates_change = on_coordinates_change;
  }

  async initialize() {
    const L = getLeaflet();
    if (!L) return;

    if (typeof window !== "undefined") {
      await import("leaflet-draw");
    }

    this.editable_layer = new L.FeatureGroup();
    this.map.addLayer(this.editable_layer);

    this.draw_control = new L.Control.Draw({
      draw: {
        rectangle: {
          shapeOptions: {
            color: "#1976D2",
            weight: 2,
            fillColor: "#FFFFFF",
            fillOpacity: 0,
            clickable: false,
          },
        },
        polyline: false,
        polygon: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
      edit: false,
    });

    const L_draw = L as any;
    if (L_draw.Draw) {
      this.map.on(L_draw.Draw.Event.CREATED, (e: any) => {
        const layer = e.layer as Rectangle;
        this.handle_rectangle_complete(layer);
      });

      this.map.on(L_draw.Draw.Event.DRAWSTART, () => {
        this.clear_rectangle();
      });
    }
  }

  private handle_rectangle_complete(rectangle: Rectangle) {
    if (this.current_rectangle && this.editable_layer) {
      this.editable_layer.removeLayer(this.current_rectangle);
    }

    this.current_rectangle = rectangle;
    if (this.editable_layer) {
      this.editable_layer.addLayer(rectangle);
    }

    const bounds = rectangle.getBounds();
    this.map.fitBounds(bounds);
    this.update_coordinates();

    if (this.edit_control) {
      this.map.removeControl(this.edit_control);
    }

    const L = getLeaflet();
    if (!L) return;

    this.edit_control = new L.Control.Draw({
      edit: {
        featureGroup: this.editable_layer!,
        remove: false,
      },
      draw: false,
    });

    rectangle.on("edit", () => {
      this.update_coordinates();
    });
  }

  private update_coordinates() {
    if (!this.current_rectangle) return;

    const bounds = this.current_rectangle.getBounds();
    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    const coords: Coordinates = {
      north: ne.lat,
      south: sw.lat,
      east: ne.lng,
      west: sw.lng,
    };

    this.on_coordinates_change(coords);
  }

  enable_drawing() {
    if (!this.draw_control) return;

    const L = getLeaflet();
    if (!L) return;

    this.clear_rectangle();
    this.draw_control.addTo(this.map);
    
    const L_draw = L as any;
    const drawRectangle = new L_draw.Draw.Rectangle(this.map, {
      shapeOptions: {
        color: "#1976D2",
        weight: 2,
        fillColor: "#FFFFFF",
        fillOpacity: 0,
        clickable: false,
      },
    });
    drawRectangle.enable();
  }

  clear_rectangle() {
    if (this.current_rectangle && this.editable_layer) {
      this.editable_layer.removeLayer(this.current_rectangle);
      this.current_rectangle = null;
    }
    if (this.draw_control) {
      this.map.removeControl(this.draw_control);
    }
    if (this.edit_control) {
      this.map.removeControl(this.edit_control);
    }
    this.on_coordinates_change(null);
  }

  get_coordinates(): Coordinates | null {
    if (!this.current_rectangle) return null;

    const bounds = this.current_rectangle.getBounds();
    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    return {
      north: ne.lat,
      south: sw.lat,
      east: ne.lng,
      west: sw.lng,
    };
  }
}
