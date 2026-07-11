import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./app/app";
import "@fontsource/figtree/400.css";
import "@fontsource/figtree/700.css";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
