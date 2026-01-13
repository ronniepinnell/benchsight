# Chrome Debugging Guide - Fix Display Issues

## Quick Checklist for Chrome

### 1. **Open Chrome DevTools**
- Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- Or right-click → "Inspect"

### 2. **Check Console Tab**
Look for **red errors**. Common issues:
- ❌ `Failed to load resource` - CSS/JS files not loading
- ❌ `SyntaxError` - JavaScript compilation error
- ❌ `Cannot read property` - Runtime error
- ❌ `Module not found` - Import error

**What to do:** Copy any red errors and share them.

### 3. **Check Network Tab**
1. Go to **Network** tab in DevTools
2. Refresh the page (`Cmd+R` / `Ctrl+R`)
3. Look for:
   - ❌ **Red entries** (failed requests)
   - ❌ Missing CSS files (`.css` files with 404 status)
   - ❌ Missing JS files (`.js` files with 404 status)

**What to do:** Check if `/_next/static/css/...` files are loading (should be 200 status).

### 4. **Clear Browser Cache**
1. Press `Cmd+Shift+Delete` (Mac) / `Ctrl+Shift+Delete` (Windows)
2. Select "Cached images and files"
3. Click "Clear data"
4. **OR** Hard refresh: `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)

### 5. **Check JavaScript is Enabled**
1. Go to `chrome://settings/content/javascript`
2. Make sure JavaScript is **Allowed**
3. Check if any extensions are blocking scripts

### 6. **Disable Extensions (Temporarily)**
Some extensions can break Next.js:
1. Go to `chrome://extensions/`
2. Toggle off extensions one by one
3. Refresh page after each toggle
4. Common culprits: Ad blockers, privacy extensions

### 7. **Check the URL**
Make sure you're visiting:
- ✅ `http://localhost:3000/analytics/overview`
- ❌ NOT `http://localhost:3000/prototypes/macro/league-overview` (old route)

### 8. **Verify Dev Server is Running**
In your terminal, you should see:
```
✓ Ready in 3.3s
✓ Compiled /analytics/overview in 500ms
```

If you see errors, the page won't load properly.

## Most Common Issues

### Issue: White Page, No Styling
**Cause:** CSS not loading or compilation error

**Fix:**
1. Check Console for errors
2. Check Network tab for failed CSS loads
3. Clear Next.js cache: `rm -rf .next` in `ui/dashboard`
4. Restart dev server: `npm run dev`

### Issue: Layout Missing (No Sidebar)
**Cause:** Route group layout not applying

**Fix:**
1. Verify URL is correct (`/analytics/overview` not `/prototypes/...`)
2. Check Console for React errors
3. Verify `(dashboard)/layout.tsx` exists

### Issue: JavaScript Errors
**Cause:** Code errors preventing render

**Fix:**
1. Check Console tab for exact error
2. Fix the error in the code
3. Restart dev server

## Quick Test

1. Open Chrome DevTools (F12)
2. Go to **Console** tab
3. Refresh page
4. **Share any red errors** you see

This will tell us exactly what's wrong!
