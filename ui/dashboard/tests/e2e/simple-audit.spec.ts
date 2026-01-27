import { test, expect } from '@playwright/test';

/**
 * Simple Dashboard Page Audit Tests
 * Tests basic page accessibility without complex redirects
 */

// Pages that should load without auth
const publicPages = [
  { name: 'Login', route: '/login' },
  { name: 'Players List', route: '/norad/players' },
  { name: 'Teams List', route: '/norad/teams' },
  { name: 'Games List', route: '/norad/games' },
  { name: 'Goalies List', route: '/norad/goalies' },
  { name: 'Leaders', route: '/norad/leaders' },
  { name: 'Schedule', route: '/norad/schedule' },
  { name: 'Analytics Overview', route: '/norad/analytics/overview' },
  { name: 'Player Compare', route: '/norad/players/compare' },
  { name: 'Team Compare', route: '/norad/teams/compare' },
  { name: 'Goalie Compare', route: '/norad/goalies/compare' },
];

test.describe('Simple Page Load Audit', () => {
  for (const page of publicPages) {
    test(`${page.name} loads`, async ({ page: browserPage }) => {
      const response = await browserPage.goto(page.route, {
        waitUntil: 'domcontentloaded',
        timeout: 15000
      });

      // Check response status
      const status = response?.status() ?? 0;
      console.log(`${page.name}: Status ${status}`);

      // Accept 200 or redirect statuses
      expect(status).toBeLessThan(400);

      // Check page has content
      const title = await browserPage.title();
      console.log(`${page.name}: Title "${title}"`);
    });
  }
});

// Analytics pages
const analyticsPages = [
  'overview', 'xg', 'war', 'micro-stats', 'zone',
  'faceoffs', 'shifts', 'rushes', 'shot-chains',
  'lines', 'statistics', 'teams', 'trends'
];

test.describe('Analytics Pages Audit', () => {
  for (const pageName of analyticsPages) {
    test(`Analytics ${pageName} loads`, async ({ page }) => {
      const response = await page.goto(`/norad/analytics/${pageName}`, {
        waitUntil: 'domcontentloaded',
        timeout: 15000
      });
      expect(response?.status() ?? 0).toBeLessThan(400);
    });
  }
});
