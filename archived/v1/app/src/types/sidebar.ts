export interface BoundingBox {
  southWest: { lat: number; lng: number };
  northEast: { lat: number; lng: number };
}

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
    highway?: string;
    name?: string;
  };
}

interface BridgeCoordinate {
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
}

export interface BridgeData {
  bridge_coordinates: BridgeCoordinate[];
}

export interface SidebarProps {
  boundingBox: BoundingBox | null;
  setBoundingBox: (box: BoundingBox | null) => void;
  setNetworkNodes: (nodes: NetworkNode[]) => void;
  setNetworkWays: (ways: NetworkWay[]) => void;
  visualizationFilter: VisualizationFilter;
  setVisualizationFilter: (filter: VisualizationFilter | ((prev: VisualizationFilter) => VisualizationFilter)) => void;
  setBridgeData: (data: BridgeData | null) => void;
  networkWays: NetworkWay[];
  networkNodes: NetworkNode[];
  metaNetwork: { nodes: { id: number; lat: number; lon: number }[]; edges: { source: number; target: number }[] };
  setMetaNetwork: (network: { nodes: { id: number; lat: number; lon: number }[]; edges: { source: number; target: number }[] }) => void;
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
}

export interface VisualizationFilter {
  showWays: boolean;
  isMonochrome: boolean;
  roadTypes: {
    motorway: boolean;
    trunk: boolean;
    primary: boolean;
    secondary: boolean;
    tertiary: boolean;
    residential: boolean;
    unclassified: boolean;
  };
  viewMode: "network-only" | "bridges-only" | "network-and-bridges" | null;
}
