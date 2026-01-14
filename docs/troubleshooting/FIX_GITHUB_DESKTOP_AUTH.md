# Fix GitHub Desktop Authentication

## The Problem
Getting authentication errors in GitHub Desktop app.

## Solution: Update Credentials in GitHub Desktop

### Option 1: Re-authenticate in GitHub Desktop

**1. Open GitHub Desktop**

**2. Go to Preferences/Settings:**
- **macOS:** `GitHub Desktop` → `Preferences` (or `Cmd + ,`)
- **Windows:** `File` → `Options`

**3. Go to Accounts tab**

**4. Sign out and sign back in:**
- Click "Sign out"
- Click "Sign in" 
- Choose "Sign in with browser" (recommended)
- This will open your browser to authenticate

**5. After signing in, try pushing again**

### Option 2: Use Personal Access Token in GitHub Desktop

**1. Create a Personal Access Token:**
- Go to: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Name: `GitHub Desktop`
- Scope: `repo` (full control)
- Generate and copy the token

**2. In GitHub Desktop:**
- Go to `Preferences` → `Accounts`
- Sign out
- Sign in with token:
  - Username: `ronniepinnell`
  - Password: `[paste your token]`

### Option 3: Use Command Line Instead

If GitHub Desktop keeps having issues, you can push from command line:

**1. Open Terminal in your project:**
```bash
cd ~/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight
```

**2. Use SSH (recommended):**
```bash
# Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# If no key, generate one
ssh-keygen -t ed25519 -C "ronnie.pinnell@gmail.com"
# Press Enter 3 times

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Copy the output

# Add to GitHub: https://github.com/settings/keys
# Click "New SSH key", paste, save

# Change remote to SSH
git remote set-url origin git@github.com:ronniepinnell/benchsight.git

# Push
git push origin --force --all
```

**3. Or use token in command line:**
```bash
# Use the script
./scripts/push_with_token.sh YOUR_TOKEN

# Or manually
git remote set-url origin https://YOUR_TOKEN@github.com/ronniepinnell/benchsight.git
git push origin --force --all
```

### Option 4: Clear GitHub Desktop Cache

**1. Quit GitHub Desktop completely**

**2. Clear stored credentials:**
```bash
# macOS
rm -rf ~/Library/Application\ Support/GitHub\ Desktop

# Windows
# Delete: %APPDATA%\GitHub Desktop
```

**3. Reopen GitHub Desktop and sign in again**

## Recommended: Use Command Line for This Push

Since you're trying to force push after cleaning history, command line is more reliable:

```bash
# Navigate to project
cd ~/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight

# Use SSH (if you set it up)
git push origin --force --all

# OR use token script
./scripts/push_with_token.sh YOUR_TOKEN
```

## Quick Fix for GitHub Desktop

**Fastest solution:**
1. In GitHub Desktop: `Preferences` → `Accounts` → `Sign out`
2. `Sign in` → Choose "Sign in with browser"
3. Complete authentication in browser
4. Try pushing again

If that doesn't work, use command line - it's more reliable for force pushes after history cleanup.
