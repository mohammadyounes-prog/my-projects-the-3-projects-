# Frontend Application

This directory will house the frontend application, likely built with React and TypeScript.

## Project Structure:

```
frontend/
├── public/               # Static assets (index.html, favicon, etc.)
│   ├── index.html
│   └── favicon.ico
├── src/                  # Main application source code
│   ├── __init__.py       # (If Python-based, though unlikely for React)
│   ├── App.tsx           # Root component of the application
│   ├── index.tsx         # Entry point for the React app
│   ├── components/       # Reusable UI components
│   │   ├── __init__.py
│   │   ├── common/       # General-purpose components (Button, Input, etc.)
│   │   └── layout/       # Layout components (Header, Sidebar, Footer)
│   ├── pages/            # Page-level components
│   │   ├── __init__.py
│   │   ├── Dashboard/    # Dashboard page components (Manager, Instructor views)
│   │   ├── Settings/     # Settings page
│   │   └── Login.tsx     # Login page
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API interaction logic
│   │   ├── api.ts        # Base API configuration
│   │   └── dashboardApi.ts # Specific API calls for dashboard data
│   ├── contexts/         # React Context API providers (e.g., AuthContext, LanguageContext)
│   ├── utils/            # Utility functions
│   ├── assets/           # Images, fonts, etc.
│   ├── styles/           # Global styles and theme configuration
│   │   ├── global.css
│   │   └── theme.ts
│   └── i18n/             # Internationalization setup
│       ├── index.ts      # i18n initialization
│       ├── locales/      # Language files (JSON)
│           ├── en.json
│           └── ar.json
├── .env                  # Environment variables (API URLs, etc.)
├── .eslintrc.js          # ESLint configuration
├── .prettierrc.js        # Prettier configuration
├── tsconfig.json         # TypeScript configuration
├── package.json          # Project dependencies and scripts
└── README.md             # Project overview and setup instructions
```

## Key Components:

*   **`public/index.html`**: The main HTML file where the React app is mounted.
*   **`src/index.tsx`**: The entry point that renders the root `App` component.
*   **`src/App.tsx`**: The main application component, often containing routing logic.
*   **`src/pages/`**: Components representing different views or pages of the dashboard.
*   **`src/components/`**: Reusable UI elements.
*   **`src/services/api.ts`**: Handles configuration for making API requests to the backend.
*   **`src/i18n/`**: Directory for managing language translations.
*   **`package.json`**: Defines project dependencies (e.g., `react`, `react-dom`, `axios`, `i18next`, language-specific packages) and development scripts (e.g., `start`, `build`, `lint`).
*   **`.env`**: For frontend-specific environment variables like backend API URLs and feature flags.
