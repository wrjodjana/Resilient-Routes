from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import List, Dict
from pydantic import BaseModel
import httpx
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from scipy.stats import norm
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class BridgeInfo(BaseModel):
    latitude: float
    longitude: float
    name: str  

class BridgeResponse(BaseModel):
    bridge_coordinates: List[BridgeInfo]

class CombinedResponse(BaseModel):
    bridges: List[Dict]
    earthquake: Dict

def get_filtered_bridges(dataset: str, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
    bridge_csv_path = './bridge_data/new_bridges_data.csv'
    df = pd.read_csv(bridge_csv_path)

    mask = (df['LATITUDE'] >= min_lat) & (df['LATITUDE'] <= max_lat) & \
           (df['LONGITUDE'] >= min_lng) & (df['LONGITUDE'] <= max_lng)
    filtered_df = df[mask]

    bridges = []
    for _, row in filtered_df.iterrows():
        bridges.append({
            "name": str(row["STRUCTURE_NUMBER_008"]),
            "year_built": str(row["YEAR_BUILT_027"]),
            "latitude": float(row["LATITUDE"]),
            "longitude": float(row["LONGITUDE"]),
            "SLIGHT_MEDIAN": float(row["SLIGHT_MEDIAN"]),
            "MODERATE_MEDIAN": float(row["MODERATE_MEDIAN"]),
            "EXTENSIVE_MEDIAN": float(row["EXTENSIVE_MEDIAN"]),
            "COMPLETE_MEDIAN": float(row["COMPLETE_MEDIAN"]),
            "BETA": float(row["BETA"]),
            "K_SKEW": float(row["K_SKEW"]),
            "K_3D_VAL": float(row["K_3D_VAL"]),
            "I_SHAPE": int(row["I_SHAPE"])
        })
    
    return bridges

async def fetch_shakemap_data(earthquake: Dict, user_magnitude: float) -> Dict:
    event_id = earthquake["id"]
    event_url = f"https://earthquake.usgs.gov/earthquakes/eventpage/{event_id}/shakemap/intensity"
        
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto(event_url)
        await page.wait_for_load_state('networkidle')
        
        content = await page.content()
        
        pattern = r"product/shakemap/([^/]+)/([^/]+)/(\d+)/download/info.json"
        match = re.search(pattern, content)
        
        await browser.close()
        
        event_code = match.group(1)    
        network = match.group(2)      
        timestamp = match.group(3)      
        
        shakemap_url = f"https://earthquake.usgs.gov/product/shakemap/{event_code}/{network}/{timestamp}/download/info.json"
        
        async with httpx.AsyncClient() as client:
            shakemap_response = await client.get(shakemap_url)
            
            shakemap_data = shakemap_response.json()
            ground_motions = shakemap_data.get("output", {}).get("ground_motions", {})
            
            return {
                "id": event_id,
                "actual_magnitude": earthquake["properties"]["mag"],
                "user_magnitude": user_magnitude,
                "location": earthquake["properties"]["place"],
                "time": earthquake["properties"]["time"],
                "depth": earthquake["geometry"]["coordinates"][2],
                "latitude": earthquake["geometry"]["coordinates"][1],
                "longitude": earthquake["geometry"]["coordinates"][0],
                "vs30": float(shakemap_data["processing"]["site_response"]["vs30default"]),
                "ground_motions": {
                    "PGA": ground_motions.get("PGA", {}) and {
                        "units": ground_motions["PGA"].get("units"),
                        "max": ground_motions["PGA"].get("max"),
                        "max_grid": ground_motions["PGA"].get("max_grid"),
                        "bias": ground_motions["PGA"].get("bias"),
                    },
                    "PGV": ground_motions.get("PGV", {}) and {
                        "units": ground_motions["PGV"].get("units"),
                        "max": ground_motions["PGV"].get("max"),
                        "max_grid": ground_motions["PGV"].get("max_grid"),
                        "bias": ground_motions["PGV"].get("bias"),
                    },
                    "MMI": ground_motions.get("MMI", {}) and {
                        "units": ground_motions["MMI"].get("units"),
                        "max": ground_motions["MMI"].get("max"),
                        "max_grid": ground_motions["MMI"].get("max_grid"),
                        "bias": ground_motions["MMI"].get("bias"),
                    },
                    "SA03": ground_motions.get("SA(0.3)", {}) and {
                        "units": ground_motions["SA(0.3)"].get("units"),
                        "max": ground_motions["SA(0.3)"].get("max"),
                        "max_grid": ground_motions["SA(0.3)"].get("max_grid"),
                        "bias": ground_motions["SA(0.3)"].get("bias"),
                    },
                    "SA10": ground_motions.get("SA(1.0)", {}) and {
                        "units": ground_motions["SA(1.0)"].get("units"),
                        "max": ground_motions["SA(1.0)"].get("max"),
                        "max_grid": ground_motions["SA(1.0)"].get("max_grid"),
                        "bias": ground_motions["SA(1.0)"].get("bias"),
                    },
                }
            }

@app.get("/data/combined-info/{dataset}")
async def get_combined_info(
    dataset: str,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    user_magnitude: float = 6.0,
    perform_seismic_analysis: bool = False
):
    try:
        bridges = get_filtered_bridges(dataset, min_lat, max_lat, min_lng, max_lng)

        center_lat = (min_lat + max_lat) / 2
        center_lng = (min_lng + max_lng) / 2
        
        search_radius = 1000
        current_time = datetime.now(timezone.utc)
        end_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        start_time = datetime(current_time.year - 50, 1, 1, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                earthquake_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}&latitude={center_lat}&longitude={center_lng}&maxradiuskm={search_radius}&minmagnitude={user_magnitude}&maxmagnitude={user_magnitude + 1}&limit=1&eventtype=earthquake"
                
                earthquake_response = await client.get(earthquake_url)
                
                earthquake_data = earthquake_response.json()
                print(earthquake_data)
                
                nearest_earthquake = earthquake_data["features"][0]
                
                try:
                    earthquake_info = await fetch_shakemap_data(nearest_earthquake, user_magnitude)
                except HTTPException as e:
                    earthquake_info = {
                        "id": nearest_earthquake["id"],
                        "actual_magnitude": nearest_earthquake["properties"]["mag"],
                        "user_magnitude": user_magnitude,
                        "location": nearest_earthquake["properties"]["place"],
                        "time": nearest_earthquake["properties"]["time"],
                        "depth": nearest_earthquake["geometry"]["coordinates"][2],
                        "latitude": nearest_earthquake["geometry"]["coordinates"][1],
                        "longitude": nearest_earthquake["geometry"]["coordinates"][0],
                    }
                
                if perform_seismic_analysis and earthquake_info.get("ground_motions"):
                    analyzed_bridges = []
                    for bridge in bridges:
                        lat1, lon1 = earthquake_info['latitude'], earthquake_info['longitude']
                        lat2, lon2 = bridge['latitude'], bridge['longitude']
                        
                        lat1, lon1 = math.radians(lat1), math.radians(lon1)
                        lat2, lon2 = math.radians(lat2), math.radians(lon2)
                        
                        dlon = lon2 - lon1
                        dlat = lat2 - lat1
                        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        R_earth = 6371
                        distance = R_earth * c

                        sa03_orig = float(earthquake_info["ground_motions"]["SA03"]["max"])
                        sa10_orig = float(earthquake_info["ground_motions"]["SA10"]["max"])

                        vs30 = earthquake_info["vs30"]
                        scaled_sa03, scaled_sa10 = scale_spectral_values(
                            sa03_orig,
                            sa10_orig,
                            earthquake_info['actual_magnitude'],
                            user_magnitude,
                            distance,
                            VS30=vs30
                        )

                        medians = np.array([
                            bridge['SLIGHT_MEDIAN'],
                            bridge['MODERATE_MEDIAN'],
                            bridge['EXTENSIVE_MEDIAN'],
                            bridge['COMPLETE_MEDIAN']
                        ])
                        beta = bridge['BETA']
                        
                        K_skew = bridge['K_SKEW']
                        K_3D = bridge['K_3D_VAL']
                        I_shape = bridge['I_SHAPE']
                        K_shape = 2.5 * sa10_orig / sa03_orig if sa03_orig > 0 else 1.0
                        
                        if I_shape == 0:
                            slight_factor = 1
                        elif I_shape == 1:
                            slight_factor = min(1, K_shape)
                            
                        medians_modify = medians.copy()
                        medians_modify[0] = medians[0] * slight_factor
                        medians_modify[1] = medians[1] * K_skew * K_3D
                        medians_modify[2] = medians[2] * K_skew * K_3D
                        medians_modify[3] = medians[3] * K_skew * K_3D
                        
                        damage_probs = [
                            norm.cdf(np.log(sa10_orig/median)/beta)
                            for median in medians_modify
                        ]
                        
                        analyzed_bridge = {
                            **bridge,
                            'damage_probabilities': {
                                'slight': damage_probs[0],
                                'moderate': damage_probs[1],
                                'extensive': damage_probs[2],
                                'complete': damage_probs[3]
                            }
                        }
                        analyzed_bridges.append(analyzed_bridge)

                    return {
                        'earthquake': earthquake_info,
                        'bridges': analyzed_bridges
                    }
                
                return {
                    "bridges": bridges,
                    "earthquake": earthquake_info
                }

        except httpx.RequestError as e:
            print(f"USGS API request error: {str(e)}")
            return {
                "bridges": bridges,
                "earthquake": None
            }

    except Exception as e:
        print(f"Error in get_combined_info: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing combined data: {str(e)}"
        )


def cal_GK15(M, R, VS30, Bdepth, F, Q_0, flag='m'):
    amp = 1 if flag == 'm' else 1/1.12
    c1, c2, c3, c4, c5 = 0.14, -6.25, 0.37, 2.237, -7.542
    c6, c7, c8, c9, c10 = -0.125, 1.19, -6.15, 0.6, 0.345
    bv, VA = -0.24, 484.5
    m1, m2, m3, m4 = -0.0012, -0.38, 0.0006, 3.9
    a1, a2, a3 = 0.01686, 1.2695, 0.0001
    Dsp = 0.75
    t1, t2, t3, t4 = 0.001, 0.59, -0.0005, -2.3
    s1, s2, s3 = 0.001, 0.077, 0.3251

    G1 = np.log(( c1 * np.arctan(M + c2) + c3) * F)
    Ro = c4*M + c5
    Do = c6 * np.cos(c7 * (M + c8)) + c9
    G2 = -0.5 * np.log((1-R/Ro)**2 + 4 * (Do**2) * (R/Ro))
    G3 = -c10 * R / Q_0
    G4 = bv * np.log(VS30 / VA)
    A_Bdepth = 1.077/np.sqrt((1-(1.5/(Bdepth+0.1))**2)**2+4*0.7**2*(1.5/(Bdepth+0.1))**2)
    A_Bdist = 1/np.sqrt((1-(40/(R+0.1))**2)**2+4*0.7**2*(40/(R+0.1))**2)
    G5 = np.log(1 + A_Bdepth * A_Bdist)
    InPGA = G1 + G2 + G3 + G4 + G5
    PGA = np.exp(InPGA) * amp

    I = (a1*M+a2)*np.exp(a3*R)
    mu = m1*R + m2*M + m3*VS30 + m4
    S = s1*R - (s2*M + s3)
    Tsp_o = np.max([0.3, np.abs(t1*R + t2*M + t3*VS30 + t4)])
    zay = 1.763-0.25*np.arctan(1.4*(Bdepth-1))
    
    t = 0.3
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_03 = Y*np.exp(InPGA)*amp

    t = 1.0
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_10 = Y*np.exp(InPGA)*amp

    return PGA, SA_03, SA_10

def scale_spectral_values(sa03_original, sa10_original, original_mag, target_mag, R, VS30, Bdepth=0.75, F=1.0, Q_0=150):
    _, sa03_orig_calc, sa10_orig_calc = cal_GK15(original_mag, R, VS30, Bdepth, F, Q_0)
    _, sa03_target_calc, sa10_target_calc = cal_GK15(target_mag, R, VS30, Bdepth, F, Q_0)
    
    sa03_scale = sa03_target_calc / sa03_orig_calc if sa03_orig_calc > 0 else 1.0
    sa10_scale = sa10_target_calc / sa10_orig_calc if sa10_orig_calc > 0 else 1.0
    
    sa03_scaled = sa03_original * sa03_scale
    sa10_scaled = sa10_original * sa10_scale
    
    return sa03_scaled, sa10_scaled

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)