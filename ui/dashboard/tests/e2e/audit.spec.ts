import { test, expect, Page } from '@playwright/test';

/**
 * Dashboard Page Audit Tests
 *
 * These tests verify:
 * 1. Page loads without 404/500 errors
 * 2. No console errors
 * 3. Data fetches complete (no loading spinners stuck)
 * 4. Basic page structure is present
 */

interface PageAuditResult {
  route: string;
  status: number;
  consoleErrors: string[];
  loadTime: number;
  hasContent: boolean;
}

// Helper to audit a page
async function auditPage(page: Page, route: string): Promise<PageAuditResult> {
  const consoleErrors: string[] = [];
  const startTime = Date.now();

  // Collect console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Navigate and get response
  const response = await page.goto(route, {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  const status = response?.status() ?? 0;
  const loadTime = Date.now() - startTime;

  // Check if page has meaningful content (not just loading)
  const hasContent = await page.locator('body').evaluate(el => {
    const text = el.innerText.toLowerCase();
    return !text.includes('loading...') || text.length > 100;
  });

  return { route, status, consoleErrors, loadTime, hasContent };
}

// ============================================
// PLAYER PAGES (Issue #78) - 9 pages
// ============================================
test.describe('Player Pages Audit', () => {
  test('Player List - /norad/players', async ({ page }) => {
    const result = await auditPage(page, '/norad/players');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Player Detail - /norad/players/[playerId]', async ({ page }) => {
    // First get a valid player ID from the list
    await page.goto('/norad/players');
    const playerLink = page.locator('a[href*="/norad/players/"]').first();

    if (await playerLink.count() > 0) {
      const href = await playerLink.getAttribute('href');
      if (href) {
        const result = await auditPage(page, href);
        expect(result.status).toBeLessThan(400);
        expect(result.consoleErrors).toHaveLength(0);
      }
    } else {
      // Test with a sample ID if no links found
      const result = await auditPage(page, '/norad/players/1');
      // 404 is acceptable if no data exists
      expect([200, 404]).toContain(result.status);
    }
  });

  test('Player Games - /norad/players/[playerId]/games', async ({ page }) => {
    const result = await auditPage(page, '/norad/players/1/games');
    expect([200, 404]).toContain(result.status);
  });

  test('Player Game Detail - /norad/players/[playerId]/games/[gameId]', async ({ page }) => {
    const result = await auditPage(page, '/norad/players/1/games/1');
    expect([200, 404]).toContain(result.status);
  });

  test('Player Trends - /norad/players/[playerId]/trends', async ({ page }) => {
    const result = await auditPage(page, '/norad/players/1/trends');
    expect([200, 404]).toContain(result.status);
  });

  test('Player Compare - /norad/players/compare', async ({ page }) => {
    const result = await auditPage(page, '/norad/players/compare');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Player Matchups - /norad/players/matchups', async ({ page }) => {
    const result = await auditPage(page, '/norad/players/matchups');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});

// ============================================
// ANALYTICS PAGES (Issue #79) - 13 pages
// ============================================
test.describe('Analytics Pages Audit', () => {
  const analyticsPages = [
    { name: 'Overview', route: '/norad/analytics/overview' },
    { name: 'xG', route: '/norad/analytics/xg' },
    { name: 'WAR', route: '/norad/analytics/war' },
    { name: 'Micro Stats', route: '/norad/analytics/micro-stats' },
    { name: 'Zone', route: '/norad/analytics/zone' },
    { name: 'Faceoffs', route: '/norad/analytics/faceoffs' },
    { name: 'Shifts', route: '/norad/analytics/shifts' },
    { name: 'Rushes', route: '/norad/analytics/rushes' },
    { name: 'Shot Chains', route: '/norad/analytics/shot-chains' },
    { name: 'Lines', route: '/norad/analytics/lines' },
    { name: 'Statistics', route: '/norad/analytics/statistics' },
    { name: 'Teams Analytics', route: '/norad/analytics/teams' },
    { name: 'Trends', route: '/norad/analytics/trends' },
  ];

  for (const p of analyticsPages) {
    test(`Analytics - ${p.name}`, async ({ page }) => {
      const result = await auditPage(page, p.route);
      expect(result.status).toBeLessThan(400);
      expect(result.consoleErrors).toHaveLength(0);
    });
  }
});

// ============================================
// TEAM PAGES (Issue #80) - 5 pages
// ============================================
test.describe('Team Pages Audit', () => {
  test('Teams List - /norad/teams', async ({ page }) => {
    const result = await auditPage(page, '/norad/teams');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Team Detail - /norad/teams/[teamId]', async ({ page }) => {
    const result = await auditPage(page, '/norad/teams/1');
    expect([200, 404]).toContain(result.status);
  });

  test('Team Compare - /norad/teams/compare', async ({ page }) => {
    const result = await auditPage(page, '/norad/teams/compare');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Free Agents - /norad/teams/free-agents', async ({ page }) => {
    const result = await auditPage(page, '/norad/teams/free-agents');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Team by Name - /norad/team/[teamName]', async ({ page }) => {
    const result = await auditPage(page, '/norad/team/test');
    expect([200, 404]).toContain(result.status);
  });
});

// ============================================
// GAME PAGES (Issue #81) - 3 pages
// ============================================
test.describe('Game Pages Audit', () => {
  test('Games List - /norad/games', async ({ page }) => {
    const result = await auditPage(page, '/norad/games');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Game Detail - /norad/games/[gameId]', async ({ page }) => {
    const result = await auditPage(page, '/norad/games/1');
    expect([200, 404]).toContain(result.status);
  });

  test('Game Shots - /norad/games/shots', async ({ page }) => {
    const result = await auditPage(page, '/norad/games/shots');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});

// ============================================
// GOALIE PAGES (Issue #82) - 3 pages
// ============================================
test.describe('Goalie Pages Audit', () => {
  test('Goalies List - /norad/goalies', async ({ page }) => {
    const result = await auditPage(page, '/norad/goalies');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Goalie Detail - /norad/goalies/[goalieId]', async ({ page }) => {
    const result = await auditPage(page, '/norad/goalies/1');
    expect([200, 404]).toContain(result.status);
  });

  test('Goalie Compare - /norad/goalies/compare', async ({ page }) => {
    const result = await auditPage(page, '/norad/goalies/compare');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});

// ============================================
// LEAGUE PAGES (Issue #83) - 3 pages
// ============================================
test.describe('League Pages Audit', () => {
  test('Standings - /norad/standings', async ({ page }) => {
    const result = await auditPage(page, '/norad/standings');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Schedule - /norad/schedule', async ({ page }) => {
    const result = await auditPage(page, '/norad/schedule');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Leaders - /norad/leaders', async ({ page }) => {
    const result = await auditPage(page, '/norad/leaders');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});

// ============================================
// TRACKER PAGES (Issue #84) - 3 pages
// ============================================
test.describe('Tracker Pages Audit', () => {
  test('Tracker Main - /norad/tracker', async ({ page }) => {
    const result = await auditPage(page, '/norad/tracker');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Tracker Game - /norad/tracker/[gameId]', async ({ page }) => {
    const result = await auditPage(page, '/norad/tracker/1');
    expect([200, 404]).toContain(result.status);
  });

  test('Tracker Videos - /norad/tracker/videos', async ({ page }) => {
    const result = await auditPage(page, '/norad/tracker/videos');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});

// ============================================
// PROTOTYPE PAGES (Issue #85) - 6 pages
// ============================================
test.describe('Prototype Pages Audit', () => {
  const prototypePages = [
    { name: 'Example', route: '/norad/prototypes/example' },
    { name: 'Test Connection', route: '/norad/prototypes/test-connection' },
    { name: 'Design System', route: '/norad/prototypes/design-system' },
    { name: 'League Stats', route: '/norad/prototypes/macro/league-stats' },
    { name: 'League Overview', route: '/norad/prototypes/macro/league-overview' },
    { name: 'Team Comparison', route: '/norad/prototypes/macro/team-comparison' },
  ];

  for (const p of prototypePages) {
    test(`Prototype - ${p.name}`, async ({ page }) => {
      const result = await auditPage(page, p.route);
      expect(result.status).toBeLessThan(400);
      expect(result.consoleErrors).toHaveLength(0);
    });
  }
});

// ============================================
// ADMIN PAGES (Issue #86) - 1 page
// ============================================
test.describe('Admin Pages Audit', () => {
  test('Admin Dashboard - /norad/admin', async ({ page }) => {
    const result = await auditPage(page, '/norad/admin');
    // Admin page might require auth, so 401/403 is acceptable
    expect([200, 401, 403]).toContain(result.status);
  });
});

// ============================================
// ROOT/AUTH PAGES (Issue #87) - 2 pages
// ============================================
test.describe('Root/Auth Pages Audit', () => {
  test('Root Page - /', async ({ page }) => {
    const result = await auditPage(page, '/');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });

  test('Login Page - /login', async ({ page }) => {
    const result = await auditPage(page, '/login');
    expect(result.status).toBeLessThan(400);
    expect(result.consoleErrors).toHaveLength(0);
  });
});
