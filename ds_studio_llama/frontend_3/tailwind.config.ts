// import type { Config } from "tailwindcss";

// export default {
//   content: [
//     "./pages/**/*.{js,ts,jsx,tsx,mdx}",
//     "./components/**/*.{js,ts,jsx,tsx,mdx}",
//     "./app/**/*.{js,ts,jsx,tsx,mdx}",
//   ],
//   theme: {
//     extend: {
//       colors: {
//         background: "var(--background)",
//         foreground: "var(--foreground)",
//       },
//     },
//   },
//   plugins: [],
// } satisfies Config;


/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}", // For Next.js `app` directory
    "./components/**/*.{js,ts,jsx,tsx}", // Include components directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
