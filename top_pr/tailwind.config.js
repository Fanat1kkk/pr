/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./my_site/**/*.{html,js}",
    "./lk/**/*.{html,js}",
    "./templates/**/*.{html,js}",
  ],
  theme: {

    screens: {
      md: { max: "991.99px" },
      sm: { max: "767.99px" },
      xs: { max: "479.99px" },
    },
    extend: {
      container: {
        center: true,
        padding: '20px'
      },
      fontFamily: {
        lato: ['Lato', 'sans-serif'],
        poppins: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
