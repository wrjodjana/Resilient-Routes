export class CustomPopup {
  private overlay!: google.maps.OverlayView;
  private position: google.maps.LatLng;
  private container: HTMLDivElement | null = null;
  private content: string;
  private map: google.maps.Map | null = null;

  constructor(position: google.maps.LatLng, content: string) {
    this.position = position;
    this.content = content;
    this.createOverlay();
  }

  private createOverlay() {
    const OverlayView = google.maps.OverlayView;

    class Overlay extends OverlayView {
      private parent: CustomPopup;

      constructor(parent: CustomPopup) {
        super();
        this.parent = parent;
      }

      onAdd() {
        this.parent.onAdd(this);
      }

      draw() {
        this.parent.draw(this);
      }

      onRemove() {
        this.parent.onRemove();
      }
    }

    this.overlay = new Overlay(this);
  }

  onAdd(overlay: google.maps.OverlayView) {
    this.container = document.createElement("div");
    this.container.style.position = "absolute";
    this.container.style.backgroundColor = "white";
    this.container.style.border = "none";
    this.container.style.borderRadius = "4px";
    this.container.style.padding = "10px 12px";
    this.container.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
    this.container.style.fontSize = "13px";
    this.container.style.color = "#333";
    this.container.style.minWidth = "140px";
    this.container.style.zIndex = "1000";
    this.container.style.fontFamily = "Arial, sans-serif";

    this.container.innerHTML = this.content;

    const closeButton = document.createElement("div");
    closeButton.innerHTML = "×";
    closeButton.style.position = "absolute";
    closeButton.style.top = "2px";
    closeButton.style.right = "6px";
    closeButton.style.cursor = "pointer";
    closeButton.style.fontSize = "18px";
    closeButton.style.fontWeight = "normal";
    closeButton.style.color = "#999";
    closeButton.style.lineHeight = "1";
    closeButton.style.padding = "0";

    closeButton.addEventListener("click", () => {
      this.setMap(null);
    });

    this.container.appendChild(closeButton);

    const panes = overlay.getPanes();
    if (panes) {
      panes.floatPane.appendChild(this.container);
    }
  }

  draw(overlay: google.maps.OverlayView) {
    if (!this.container) return;

    const overlayProjection = overlay.getProjection();
    const position = overlayProjection.fromLatLngToDivPixel(this.position);

    if (position) {
      this.container.style.left = position.x + "px";
      this.container.style.top = position.y - this.container.offsetHeight - 10 + "px";
    }
  }

  onRemove() {
    if (this.container && this.container.parentElement) {
      this.container.parentElement.removeChild(this.container);
      this.container = null;
    }
  }

  setMap(map: google.maps.Map | null) {
    this.map = map;
    this.overlay.setMap(map);
  }

  setContent(content: string) {
    this.content = content;
    if (this.container) {
      const closeButton = this.container.querySelector("div:last-child");
      this.container.innerHTML = content;
      if (closeButton) {
        this.container.appendChild(closeButton);
      }
    }
  }

  setPosition(position: google.maps.LatLng) {
    this.position = position;
    if (this.overlay.draw) {
      this.overlay.draw();
    }
  }
}
