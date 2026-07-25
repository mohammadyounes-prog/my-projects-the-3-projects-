/**
 * Role → module matrix (pragmatic IAM for Dashboard nav / soft route guards).
 *
 * Backend sources (see backend auth):
 *   - TAMS/MySQL employees → always `"instructor"`
 *   - QuestAI SQLite `users.role` → whatever is stored (admin, executive, …)
 *
 * | Role (normalized)                    | Modules                                              |
 * |--------------------------------------|------------------------------------------------------|
 * | `admin`, `superadmin`, `super_admin` | educational, executive, corporate, weights, settings |
 * | missing / empty role                 | same as admin (safe demo default)                    |
 * | `instructor`, `teacher`, `faculty`,  | educational, settings                                |
 * |   `lecturer`                         |                                                      |
 * | contains `executive` / `exec`        | executive, settings                                  |
 * | `corporate`, contains `hr`           | corporate, settings                                  |
 * | anything else                        | settings only                                        |
 *
 * Home (`/`, `/home`) is always allowed when authenticated.
 * Weights (KPI index config) is admin-only.
 */

export type ModuleId =
  | 'educational'
  | 'executive'
  | 'corporate'
  | 'weights'
  | 'settings';

const ALL_MODULES: ModuleId[] = [
  'educational',
  'executive',
  'corporate',
  'weights',
  'settings',
];

const MODULE_PATH_PREFIXES: Record<ModuleId, string[]> = {
  educational: ['/educational'],
  executive: ['/executive-dashboard'],
  corporate: ['/corporate-dashboard'],
  weights: ['/weights'],
  settings: ['/settings'],
};

export function getRole(): string {
  const raw = localStorage.getItem('role');
  return (raw ?? '').trim().toLowerCase();
}

function isAdminRole(role: string): boolean {
  return (
    role === 'admin' ||
    role === 'superadmin' ||
    role === 'super_admin' ||
    role === 'super-admin'
  );
}

function isInstructorRole(role: string): boolean {
  return (
    role === 'instructor' ||
    role === 'teacher' ||
    role === 'faculty' ||
    role === 'lecturer'
  );
}

function isExecutiveRole(role: string): boolean {
  return (
    role === 'executive' ||
    role === 'exec' ||
    role.includes('executive')
  );
}

function isCorporateRole(role: string): boolean {
  return (
    role === 'corporate' ||
    role === 'hr' ||
    role.includes('corporate') ||
    role === 'human_resources' ||
    role === 'human-resources'
  );
}

/** Modules visible in gateway cards + header nav for the given role. */
export function visibleModules(role?: string): ModuleId[] {
  const r = (role ?? getRole()).trim().toLowerCase();

  // Missing role → all modules (safe demo default when localStorage.role unset)
  if (!r || isAdminRole(r)) {
    return [...ALL_MODULES];
  }
  if (isInstructorRole(r)) {
    return ['educational', 'settings'];
  }
  if (isExecutiveRole(r)) {
    return ['executive', 'settings'];
  }
  if (isCorporateRole(r)) {
    return ['corporate', 'settings'];
  }
  return ['settings'];
}

export function canAccessModule(module: ModuleId, role?: string): boolean {
  return visibleModules(role).includes(module);
}

function moduleForPath(pathname: string): ModuleId | null {
  const path = pathname.split('?')[0] || '/';
  for (const [mod, prefixes] of Object.entries(MODULE_PATH_PREFIXES) as [
    ModuleId,
    string[],
  ][]) {
    if (prefixes.some((p) => path === p || path.startsWith(`${p}/`))) {
      return mod;
    }
  }
  return null;
}

/**
 * Soft path guard. Home and unknown/non-module paths are allowed.
 * Module paths require the role to include that module.
 */
export function canAccess(pathOrModule: string, role?: string): boolean {
  const key = pathOrModule.trim().toLowerCase();

  if (
    key === 'educational' ||
    key === 'executive' ||
    key === 'corporate' ||
    key === 'weights' ||
    key === 'settings'
  ) {
    return canAccessModule(key as ModuleId, role);
  }

  const path = key.startsWith('/') ? key.split('?')[0] : `/${key}`;
  if (path === '/' || path === '/home') {
    return true;
  }

  const mod = moduleForPath(path);
  if (!mod) {
    return true;
  }
  return canAccessModule(mod, role);
}

/** Gateway card / nav link targets keyed by module. */
export const MODULE_LINKS: Record<
  ModuleId,
  { to: string; labelKey: string; fallback: string }
> = {
  educational: {
    to: '/educational/admins',
    labelKey: 'nav.dashboard',
    fallback: 'Educational',
  },
  executive: {
    to: '/executive-dashboard',
    labelKey: 'nav.executive',
    fallback: 'Executive',
  },
  corporate: {
    to: '/corporate-dashboard',
    labelKey: 'nav.corporate',
    fallback: 'Corporate',
  },
  weights: {
    to: '/weights',
    labelKey: 'nav.indexes_weight',
    fallback: 'Indexes Weight',
  },
  settings: {
    to: '/settings',
    labelKey: 'nav.settings',
    fallback: 'Settings',
  },
};
