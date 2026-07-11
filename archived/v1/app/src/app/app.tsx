import React from "react";
import "./app.css";
import "leaflet/dist/leaflet.css";
import { BaseMap } from "../pages/map.tsx";
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      {" "}
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BaseMap />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
