/**
 * QuestAI shared app shell — sidebar + mobile topbar.
 *
 * Replaces the old hand-copied <nav class="navbar">…</nav> block that used
 * to be duplicated verbatim across every page. Renders once, synchronously,
 * before DOMContentLoaded so auth.js / i18n.js (which run on
 * DOMContentLoaded) can operate on it exactly like they did on the old
 * static markup — same element IDs, same behavior, no changes needed there.
 *
 * Usage: include as the very first thing inside <body>, e.g.
 *   <body>
 *     <script src="shell.js"></script>
 *     ...rest of page...
 */
(function () {
  'use strict';

  var ICONS = {
    home: '<path d="M3 9.5 12 3l9 6.5"/><path d="M5 8.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V8.5"/>',
    zap: '<path d="M12 2 4 13h6l-1 9 9-11h-6l1-9z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    check: '<path d="M4 12.5l4.5 4.5L20 6"/>',
    chart: '<path d="M4 20V10"/><path d="M11 20V4"/><path d="M18 20v-7"/><path d="M3 20h18"/>',
    card: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/>',
    user: '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.3 3.1-6 7-6s7 2.7 7 6"/>',
    sliders: '<path d="M4 6h9"/><path d="M17 6h3"/><path d="M4 12h3"/><path d="M11 12h9"/><path d="M4 18h13"/><path d="M21 18h-1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    shield: '<path d="M12 3l7 3v6c0 5-4 8-7 9-3-1-7-4-7-9V6l7-3z"/>',
    tool: '<path d="M14.5 6.5 18 3l3 3-3.5 3.5"/><path d="M15.5 8.5 4 20"/><path d="M9.5 13 3 6.5 6.5 3 13 9.5"/>',
    plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
    menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    close: '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
    chevron: '<path d="M9 5l7 7-7 7"/>'
  };

  function icon(name, size) {
    size = size || 16;
    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" ' +
      'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ' +
      'aria-hidden="true" focusable="false">' + (ICONS[name] || '') + '</svg>';
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Best-effort synchronous read (no network) so admin-only links don't
  // flash-and-hide once auth.js's async /users/me check completes.
  var isAdmin = localStorage.getItem('isAdmin') === '1' || localStorage.getItem('isAdmin') === 'true';
  var isSuperAdmin = localStorage.getItem('isSuperAdmin') === '1' || localStorage.getItem('isSuperAdmin') === 'true';
  var canSeeAdmin = isAdmin || isSuperAdmin;

  var NAV_GROUPS = [
    {
      items: [
        { href: 'home.html', i18n: 'nav.home', label: 'Home', icon: 'home' }
      ]
    },
    {
      labelI18n: 'nav.groupWorkspace', label: 'Workspace',
      items: [
        { href: 'index.html', i18n: 'nav.generateQuestions', label: 'Generate Questions', icon: 'zap' },
        { href: 'tasks.html', i18n: 'nav.taskHistory', label: 'Task History', icon: 'clock' },
        { href: 'tamsQB.html', i18n: 'nav.takeATest', label: 'Take a Test', icon: 'check', navId: 'takeATestNavItem', initialDisplay: 'block' }
      ]
    },
    {
      labelI18n: 'nav.groupReports', label: 'Reports',
      items: [
        { href: 'result_report.html', i18n: 'nav.resultReport', label: 'Result Report', icon: 'chart', navId: 'resultReportNavItem', initialDisplay: 'block' }
      ]
    },
    {
      labelI18n: 'nav.groupAccount', label: 'Account',
      items: [
        { href: 'billing.html', i18n: 'nav.bundlesManagement', label: 'Bundles Management', icon: 'card' },
        { href: 'profile.html', i18n: 'nav.profile', label: 'Profile', icon: 'user' },
        { href: 'user_preferences.html', i18n: 'nav.userPreferences', label: 'User Preferences', icon: 'sliders' }
      ]
    },
    {
      labelI18n: 'nav.groupAdmin', label: 'Admin', adminOnly: true,
      items: [
        { href: 'admin_dashboard.html', i18n: 'nav.settings', label: 'Settings', icon: 'shield', navId: 'settingsNavItem', initialDisplay: canSeeAdmin ? 'block' : 'none' },
        { href: 'admin.html', i18n: 'nav.admin', label: 'Admin', icon: 'tool', navId: 'adminNavItem', initialDisplay: canSeeAdmin ? 'block' : 'none' },
        { href: 'add_question.html', i18n: 'nav.addQuestion', label: 'Add Question', icon: 'plus', adminOnly: true }
      ]
    }
  ];

  function currentPage() {
    var parts = location.pathname.split('/');
    return (parts[parts.length - 1] || 'home.html').toLowerCase();
  }

  function linkHtml(item) {
    var active = item.href.toLowerCase() === currentPage();
    var cls = 'nebula-sidebar__link' + (active ? ' nebula-sidebar__link--active' : '');
    return '<a class="' + cls + '" href="' + item.href + '"' +
      (item.i18n ? ' data-i18n="' + item.i18n + '"' : '') +
      (active ? ' aria-current="page"' : '') + '>' +
      '<span class="nebula-sidebar__link-icon">' + icon(item.icon) + '</span>' +
      '<span>' + esc(item.label) + '</span></a>';
  }

  function itemHtml(item) {
    if (item.adminOnly && !item.navId && !canSeeAdmin) {
      return ''; // not rendered at all until role is confirmed admin
    }
    if (item.navId) {
      var style = item.initialDisplay ? ' style="display:' + item.initialDisplay + ';"' : '';
      return '<div id="' + item.navId + '"' + style + '>' + linkHtml(item) + '</div>';
    }
    return linkHtml(item);
  }

  function groupHtml(group) {
    if (group.adminOnly && !canSeeAdmin) {
      // Still render the group so the two legacy-gated items (which
      // auth.js may reveal later) keep a section label to sit under.
    }
    var itemsHtml = group.items.map(itemHtml).join('');
    var labelHtml = group.label
      ? '<div class="nebula-sidebar__section-label"' + (group.labelI18n ? ' data-i18n="' + group.labelI18n + '"' : '') + '>' + esc(group.label) + '</div>'
      : '';
    return labelHtml + itemsHtml;
  }

  function sidebarHtml() {
    var groups = NAV_GROUPS.map(groupHtml).join('');
    return (
      '<aside class="nebula-sidebar" id="nebulaSidebar" aria-label="Primary navigation">' +
        '<a class="nebula-sidebar__brand" href="home.html" aria-label="QuestAI">' +
          '<span class="nebula-brand-text" data-i18n="home.brandName">QuestAI</span>' +
        '</a>' +
        '<nav class="nebula-sidebar__nav">' + groups + '</nav>' +
        '<div class="nebula-sidebar__footer">' +
          '<div class="nebula-sidebar__user-row">' +
            '<span id="currentUserName" class="nebula-sidebar__username"></span>' +
            '<select id="langSwitcher" class="form-select form-select-sm" style="width:auto;" aria-label="Language">' +
              '<option value="en">EN</option>' +
              '<option value="ar">AR</option>' +
            '</select>' +
          '</div>' +
          '<button class="nebula-btn nebula-btn--ghost nebula-btn--sm" id="logoutButton" data-i18n="nav.logout">Logout</button>' +
        '</div>' +
      '</aside>' +
      '<div class="nebula-sidebar__backdrop" id="nebulaSidebarBackdrop"></div>' +
      '<header class="nebula-topbar">' +
        '<button class="nebula-topbar__toggle" id="nebulaSidebarToggle" aria-label="Toggle navigation" aria-expanded="false">' + icon('menu', 18) + '</button>' +
        '<a class="nebula-topbar__brand" href="home.html"><span class="nebula-brand-text">QuestAI</span></a>' +
      '</header>'
    );
  }

  function setOpen(open) {
    var sidebar = document.getElementById('nebulaSidebar');
    var backdrop = document.getElementById('nebulaSidebarBackdrop');
    var toggle = document.getElementById('nebulaSidebarToggle');
    if (!sidebar || !backdrop || !toggle) return;
    sidebar.classList.toggle('nebula-sidebar--open', open);
    backdrop.classList.toggle('nebula-sidebar__backdrop--visible', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.innerHTML = icon(open ? 'close' : 'menu', 18);
  }

  function wireInteractions() {
    var toggle = document.getElementById('nebulaSidebarToggle');
    var backdrop = document.getElementById('nebulaSidebarBackdrop');
    var sidebar = document.getElementById('nebulaSidebar');
    if (toggle) {
      toggle.addEventListener('click', function () {
        setOpen(!sidebar.classList.contains('nebula-sidebar--open'));
      });
    }
    if (backdrop) {
      backdrop.addEventListener('click', function () { setOpen(false); });
    }
    if (sidebar) {
      sidebar.addEventListener('click', function (e) {
        if (e.target.closest('a.nebula-sidebar__link')) setOpen(false);
      });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });
  }

  function mount() {
    document.body.insertAdjacentHTML('afterbegin', sidebarHtml());
    document.body.classList.add('nebula-has-sidebar');
    wireInteractions();
  }

  mount();
})();
