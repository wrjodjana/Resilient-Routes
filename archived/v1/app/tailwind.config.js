/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        montserrat: ["Montserrat", "sans-serif"],
        figtree: ["Figtree", "sans-serif"],
      },
      fontWeight: {
        extralight: "200",
        medium: "500",
        semibold: "600",
        bold: "700",
      },
      fontSize: {
        xxxs: "0.6rem",
        xxs: "0.62rem",
        sl: "0.9rem",
        l: "0.93rem",
        ssxl: "1.07rem",
        sxl: "1.13rem",
        s2xl: "1.35rem",
      },
      colors: {
        footer: "#13294b",
        groundBase: "#fafafa",
        red: "#8c0305",
        lightGray: "#f5f5f7",
        lightBlue: "#a8d5e5",
        cyan: "#165a72",
      },
    },
  },
  plugins: [],
};
