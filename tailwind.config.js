/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/"],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        myDarkTheme: {
          "primary": "#8FCCD6",
          "primary-content": "#0A171A",
          "secondary": "#BDDBCC",
          "accent": "#71AAB3",
          "neutral": "#1E1F22",
          "neutral-content": "#949C9E",
          "info": "#9CC3C9",
          "base-100": "#2B2D31",
          "base-200": "#1E1F22",
          "base-300": "#8FCCD6",
          "base-content": "#E5E6E7",
          "warning": "#FBB13C",
          "error": "#CF6679",
          "success": "#6FD08C",
        },
      },
      {
        myLightTheme: {
          "primary": "#8FCCD6",
          "primary-content": "#0A171A",
          "secondary": "#BDDBCC",
          "accent": "#71AAB3",
          "neutral": "#8FCCD6",
          "neutral-content": "#545C5D",
          "info": "#9CC3C9",
          "base-100": "#E6FBFE",
          "base-200": "#D9EEF3",
          "base-300": "#545C5D",
          "base-content": "#191A1B",
          "warning": "#FBB13C",
          "error": "#F97089",
          "success": "#6FD08C",
        },
      },
    ],
  },
  safelist: [
    'alert-info',
    'alert-success',
    'alert-warning',
    'alert-error',
    'badge-info',
    'badge-success',
    'badge-warning',
    'badge-error',
    'badge-primary',
    'input',
    'form-input',
    'custom-btn',
  ],
}
