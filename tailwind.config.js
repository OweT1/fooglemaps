import { colors } from './src/themes/colors';
import { spacing, borderRadius, boxShadow } from './src/themes/spacing';

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors,
      spacing,
      borderRadius,
      boxShadow,
    },
  },
  plugins: [],
};
