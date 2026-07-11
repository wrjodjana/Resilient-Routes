export interface NetworkNode {
  id: number;
  lat: number;
  lon: number;
  tags?: {
    [key: string]: string;
  };
}

export interface NetworkWay {
  type: "way";
  id: number;
  nodes: number[];
  tags?: {
    [key: string]: string;
  };
}

export interface BridgeData {
  bridge_coordinates: {
    latitude: number;
    longitude: number;
    name: string;
    year_built: string;
    damage_probabilities?: {
      slight: number;
      moderate: number;
      extensive: number;
      complete: number;
    };
  }[];
}
