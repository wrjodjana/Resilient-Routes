import React, { useEffect } from "react";
import { useMap } from "react-leaflet";

interface MapOperationsProps {
  center: [number, number];
  zoom: number;
}

const MapOperations: React.FC<MapOperationsProps> = ({ center, zoom }) => {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
};

export default MapOperations;
