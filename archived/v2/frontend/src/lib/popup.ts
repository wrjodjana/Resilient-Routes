import type { Map, LatLngExpression, Popup } from "leaflet";
import { getLeaflet } from "./leaflet_map";

export class CustomPopup {
  private popup: Popup | null = null;
  private position: LatLngExpression;
  private content: string;
  private map: Map | null = null;

  constructor(position: LatLngExpression, content: string) {
    this.position = position;
    this.content = content;
  }

  setMap(map: Map | null) {
    this.map = map;
    
    if (map && this.popup) {
      this.popup.addTo(map);
    } else if (!map && this.popup) {
      this.popup.remove();
      this.popup = null;
    }
  }

  setContent(content: string) {
    this.content = content;
    if (this.popup) {
      this.popup.setContent(this.getFormattedContent());
    }
  }

  setPosition(position: LatLngExpression) {
    this.position = position;
    if (this.popup) {
      this.popup.setLatLng(position);
    }
  }

  private getFormattedContent(): string {
    const closeButton = '<div style="position: absolute; top: 2px; right: 6px; cursor: pointer; font-size: 18px; font-weight: normal; color: #999; line-height: 1; padding: 0;" onclick="this.closest(\'.leaflet-popup\').remove()">×</div>';
    return `<div style="position: relative; padding-right: 20px;">${this.content}${closeButton}</div>`;
  }

  show() {
    if (!this.map) return;

    const L = getLeaflet();
    if (!L) return;

    if (this.popup) {
      this.popup.remove();
    }

    this.popup = L.popup({
      className: "custom-popup",
      closeButton: false,
      autoPan: true,
      offset: [0, -10],
    })
      .setLatLng(this.position)
      .setContent(this.getFormattedContent())
      .openOn(this.map);
  }

  remove() {
    if (this.popup) {
      this.popup.remove();
      this.popup = null;
    }
  }
}
