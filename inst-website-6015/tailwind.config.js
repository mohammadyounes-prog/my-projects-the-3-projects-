/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.tsx',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--nebula-font-display)'],
        sans: ['var(--nebula-font-body)'],
      },
      colors: {
        // Legacy class names used by existing components
        'primary-blue': 'var(--nebula-accent-cyan)',
        'light-blue': 'var(--nebula-accent-cyan-dim)',
        primary: {
          DEFAULT: 'var(--nebula-accent-cyan)',
          dark: 'var(--nebula-accent-blue)',
          soft: 'var(--nebula-accent-cyan-dim)',
          50: 'var(--nebula-accent-cyan-dim)',
          500: 'var(--nebula-accent-cyan)',
          900: 'var(--nebula-accent-blue)',
        },
        surface: {
          DEFAULT: 'var(--nebula-bg-deep)',
          raised: 'var(--nebula-bg-surface)',
        },
        suite: {
          text: 'var(--nebula-text)',
          muted: 'var(--nebula-text-muted)',
          border: 'var(--nebula-border)',
          success: 'var(--nebula-success)',
          warning: 'var(--nebula-warning)',
          danger: 'var(--nebula-danger)',
        },
        nebula: {
          'bg-deep': 'var(--nebula-bg-deep)',
          'bg-surface': 'var(--nebula-bg-surface)',
          'bg-raised': 'var(--nebula-bg-raised)',
          'bg-glass': 'var(--nebula-bg-glass)',
          'bg-glass-heavy': 'var(--nebula-bg-glass-heavy)',
          'input': 'var(--nebula-bg-input)',
          'accent-cyan': 'var(--nebula-accent-cyan)',
          'accent-purple': 'var(--nebula-accent-purple)',
          'accent-blue': 'var(--nebula-accent-blue)',
          'accent-pink': 'var(--nebula-accent-pink)',
          'accent-cyan-dim': 'var(--nebula-accent-cyan-dim)',
          'accent-purple-dim': 'var(--nebula-accent-purple-dim)',
          'success': 'var(--nebula-success)',
          'success-dim': 'var(--nebula-success-dim)',
          'warning': 'var(--nebula-warning)',
          'warning-dim': 'var(--nebula-warning-dim)',
          'danger': 'var(--nebula-danger)',
          'danger-dim': 'var(--nebula-danger-dim)',
          'text': 'var(--nebula-text)',
          'text-muted': 'var(--nebula-text-muted)',
          'text-dim': 'var(--nebula-text-dim)',
          'on-accent': 'var(--nebula-on-accent)',
          'border': 'var(--nebula-border)',
          'border-strong': 'var(--nebula-border-strong)',
          'border-glow': 'var(--nebula-border-glow)',
        }
      },
      borderRadius: {
        sm: 'var(--nebula-radius-sm)',
        md: 'var(--nebula-radius-md)',
        lg: 'var(--nebula-radius-lg)',
      },
      boxShadow: {
        suite0: 'var(--nebula-shadow-0)',
        suite1: 'var(--nebula-shadow-1)',
        suite2: 'var(--nebula-shadow-2)',
        'nebula-glass': 'var(--nebula-shadow-glass)',
        'glow-cyan': 'var(--nebula-glow-cyan)',
        'glow-purple': 'var(--nebula-glow-purple)',
      },
    },
  },
  plugins: [],
};
