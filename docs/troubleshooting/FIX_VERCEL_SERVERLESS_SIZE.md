# Fix Vercel Serverless Function Size Error

**Error:** `A Serverless Function has exceeded the unzipped maximum size of 250 MB`

---

## Quick Fix

The issue is that Vercel is including too many files in the serverless function bundle. We've already fixed this by:

1. ✅ Updated `next.config.js` to exclude large files
2. ✅ Updated `.vercelignore` to exclude data directories

**Just redeploy!** The changes should fix the issue.

---

## What Was Fixed

### 1. Updated `next.config.js`

Added `outputFileTracingExcludes` to prevent Next.js from including:
- Data directories (`data/`)
- Documentation (`docs/`)
- Python files and dependencies
- Large CSV/Excel files
- Logs and archives

### 2. Updated `.vercelignore`

Added exclusions for:
- All data directories
- Documentation
- Python source files
- Large data files (CSV, Excel, JSON)
- Logs and archives

---

## Verify the Fix

### Check Build Size

After deploying, check Vercel build logs:
- Should show smaller function sizes
- Should not include data directories
- Should only include Next.js app files

### If Still Having Issues

**Option 1: Check Vercel Project Settings**

1. Go to Vercel → Your Project → Settings
2. Check **"Root Directory"** is set to `ui/dashboard`
3. This ensures Vercel only builds from the dashboard directory

**Option 2: Check for Large Dependencies**

```bash
cd ui/dashboard
npm ls --depth=0 | grep -E "large|big|heavy"
```

**Option 3: Analyze Bundle Size**

```bash
cd ui/dashboard
npm run build
# Check the build output for large files
```

---

## Prevention

### Best Practices

1. **Keep Root Directory Set:**
   - Vercel → Settings → Root Directory: `ui/dashboard`
   - This prevents including parent directory files

2. **Use .vercelignore:**
   - Always exclude data directories
   - Exclude documentation
   - Exclude build artifacts

3. **Optimize Dependencies:**
   - Remove unused packages
   - Use dynamic imports for large libraries
   - Consider code splitting

4. **Monitor Bundle Size:**
   - Check Vercel build logs regularly
   - Use Next.js bundle analyzer if needed

---

## Common Causes

### Large Files Being Included

**Problem:** Data files, docs, or Python files being bundled

**Solution:**
- ✅ Already fixed with `.vercelignore`
- ✅ Already fixed with `outputFileTracingExcludes`

### Wrong Root Directory

**Problem:** Vercel building from project root instead of `ui/dashboard`

**Solution:**
- Set Root Directory in Vercel settings
- Should be: `ui/dashboard`

### Large Dependencies

**Problem:** npm packages adding too much to bundle

**Solution:**
- Review `package.json` dependencies
- Remove unused packages
- Use dynamic imports for large libraries

---

## Troubleshooting

### "Still getting size error after fix"

**Check:**
1. Did you commit and push the changes?
2. Did Vercel redeploy with the new config?
3. Check build logs for what's being included

**Fix:**
```bash
# Verify files are committed
git status

# Push changes
git add ui/dashboard/next.config.js ui/dashboard/.vercelignore
git commit -m "fix: exclude large files from Vercel serverless functions"
git push origin develop

# Trigger new deployment
# Or wait for auto-deploy
```

### "Build succeeds but function is still large"

**Check:**
- Are there large files in `public/` directory?
- Are there large static assets?
- Check Vercel build logs for file sizes

**Fix:**
- Move large assets to CDN (Supabase Storage, etc.)
- Use external image hosting
- Optimize images

### "Can't find .vercelignore"

**Location:**
- Should be in `ui/dashboard/.vercelignore`
- Not in project root

**Create if missing:**
```bash
cd ui/dashboard
# Copy the updated .vercelignore content
```

---

## Additional Optimizations

### Dynamic Imports

For large libraries, use dynamic imports:

```typescript
// Instead of:
import LargeLibrary from 'large-library'

// Use:
const LargeLibrary = dynamic(() => import('large-library'), {
  ssr: false
})
```

### Code Splitting

Next.js automatically code splits, but you can optimize:

```typescript
// Use React.lazy for large components
const HeavyComponent = React.lazy(() => import('./HeavyComponent'))
```

### Image Optimization

Use Next.js Image component with external hosting:

```typescript
import Image from 'next/image'

<Image
  src="https://your-cdn.com/image.jpg"
  width={500}
  height={300}
  alt="Description"
/>
```

---

## Verification Checklist

After deploying:

- [ ] Build succeeds without size errors
- [ ] Function size is under 250 MB
- [ ] Dashboard loads correctly
- [ ] No missing assets
- [ ] API routes work
- [ ] Supabase connection works

---

## Related Documentation

- [Vercel Serverless Function Limits](https://vercel.com/docs/functions/serverless-functions/runtimes#limits)
- [Next.js Output File Tracing](https://nextjs.org/docs/app/api-reference/next-config-js/output#outputfiletracingexcludes)
- [Vercel Build Configuration](https://vercel.com/docs/build-step)

---

*Last updated: 2026-01-13*
