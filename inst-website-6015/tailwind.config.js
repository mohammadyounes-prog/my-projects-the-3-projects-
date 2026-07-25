/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.tsx',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--suite-font-display)'],
        sans: ['var(--suite-font-body)'],
      },
      colors: {
        // Legacy class names used by existing components — aliased to suite
        'primary-blue': 'var(--suite-primary)',
        'light-blue': 'var(--suite-primary-soft)',
        primary: {
          DEFAULT: 'var(--suite-primary)',
          dark: 'var(--suite-primary-dark)',
          soft: 'var(--suite-primary-soft)',
          50: 'var(--suite-primary-soft)',
          500: 'var(--suite-primary)',
          900: 'var(--suite-primary-dark)',
        },
        surface: {
          DEFAULT: 'var(--suite-surface)',
          raised: 'var(--suite-surface-raised)',
        },
        suite: {
          text: 'var(--suite-text)',
          muted: 'var(--suite-text-muted)',
          border: 'var(--suite-border)',
          success: 'var(--suite-success)',
          warning: 'var(--suite-warning)',
          danger: 'var(--suite-danger)',
        },
      },
      borderRadius: {
        sm: 'var(--suite-radius-sm)',
        md: 'var(--suite-radius-md)',
        lg: 'var(--suite-radius-lg)',
      },
      boxShadow: {
        suite0: 'var(--suite-shadow-0)',
        suite1: 'var(--suite-shadow-1)',
        suite2: 'var(--suite-shadow-2)',
      },
    },
  },
  plugins: [],
};
