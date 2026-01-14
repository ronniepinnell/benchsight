# Fix Deployment Errors

## Issue: ESLint Version Conflict

**Error:** `eslint-config-next@16.1.1` requires `eslint@>=9.0.0` but project has `eslint@^8`

## Solution Applied

1. ✅ **Updated `package.json`** - Changed `eslint` from `^8` to `^9`
2. ✅ **Updated `vercel.json`** - Added `--legacy-peer-deps` to install command
3. ✅ **Created `.npmrc`** - Added `legacy-peer-deps=true` as fallback

## Next Steps

1. **Commit and push changes:**
   ```bash
   git add ui/dashboard/package.json ui/dashboard/vercel.json ui/dashboard/.npmrc
   git commit -m "Fix ESLint version conflict for deployment"
   git push
   ```

2. **Redeploy on Vercel:**
   - Vercel will automatically redeploy on push
   - Or manually trigger redeploy in Vercel dashboard

## If Still Failing

### Option 1: Use Legacy Peer Deps (Already Applied)
The `.npmrc` file should handle this automatically.

### Option 2: Update ESLint Config
If Next.js 16 requires ESLint 9 flat config, you may need to update ESLint config:

```javascript
// eslint.config.js (if needed)
import { FlatCompat } from '@eslint/eslintrc';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
];
```

### Option 3: Downgrade Next.js (Not Recommended)
If you want to stick with ESLint 8:
- Downgrade to Next.js 14
- Use `eslint-config-next@14.x`

## Verification

After deployment succeeds:
- ✅ Build completes without errors
- ✅ Site loads at Vercel URL
- ✅ All pages accessible
