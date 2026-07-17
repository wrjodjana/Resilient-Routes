import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Resilient Routes",
  description: "Seismic reliability of transportation networks: which locations stay connected to the critical destination after an earthquake.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
