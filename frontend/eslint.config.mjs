import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

/**
 * Flat ESLint config (ESLint 9 + eslint-config-next 16).
 *
 * Next.js 16 no longer ships `next lint`, so lint runs through the ESLint CLI.
 * The React Compiler rules bundled with eslint-config-next 16 are reported as
 * warnings for now: this codebase predates them and they are advisory, while
 * correctness rules (no-undef, hooks ordering, a11y) stay errors and gate CI.
 */
const config = [
  ...nextCoreWebVitals,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    rules: {
      "react/no-unescaped-entities": "off",
      "react-hooks/exhaustive-deps": "warn",
      "react-hooks/set-state-in-effect": "warn",
      "react-hooks/immutability": "warn",
      "react-hooks/preserve-manual-memoization": "warn",
      "react-hooks/refs": "warn",
    },
  },
  {
    ignores: [".next/**", "node_modules/**", "next-env.d.ts", "out/**"],
  },
];

export default config;
