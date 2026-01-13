# Push from Command Line (Bypass GitHub Desktop)

Since GitHub Desktop is having auth issues, use command line instead.

## Quick Steps

### 1. Open Terminal and Navigate to Project

```bash
cd ~/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight
```

### 2. Choose Your Method

**Option A: Use SSH (Best - No Token Needed)**

```bash
# Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# If no key, generate one (press Enter 3 times)
ssh-keygen -t ed25519 -C "ronnie.pinnell@gmail.com"

# Copy your public key
cat ~/.ssh/id_ed25519.pub
# Copy the entire output

# Add to GitHub:
# 1. Go to: https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste your public key
# 4. Save

# Change remote to SSH
git remote set-url origin git@github.com:ronniepinnell/benchsight.git

# Test connection
ssh -T git@github.com
# Should say: "Hi ronniepinnell! You've successfully authenticated..."

# Push (no password needed!)
git push origin --force --all
```

**Option B: Use Personal Access Token**

```bash
# Get token from: https://github.com/settings/tokens
# Generate new token (classic), scope: repo

# Use the script
./scripts/push_with_token.sh YOUR_TOKEN_HERE

# OR manually
git remote set-url origin https://YOUR_TOKEN@github.com/ronniepinnell/benchsight.git
git push origin --force --all
git remote set-url origin https://github.com/ronniepinnell/benchsight.git
```

**Option C: Use Credential Helper**

```bash
# Clear old credentials
security delete-internet-password -s github.com

# Make sure credential helper is set
git config credential.helper osxkeychain

# Push (will prompt once)
git push origin --force --all
# Username: ronniepinnell
# Password: [paste your token]
```

## After Pushing

GitHub Desktop should sync automatically, or you can:
- In GitHub Desktop: `Repository` → `Pull` to sync
- Or just close and reopen GitHub Desktop

## Why Command Line is Better for This

- More reliable for force pushes
- Better error messages
- Can use SSH (no token needed)
- Works even if GitHub Desktop has issues

## Recommended: Set Up SSH

SSH is the most reliable long-term solution:
- No tokens to manage
- Works everywhere
- More secure
- Never expires

Once set up, both command line AND GitHub Desktop will work seamlessly.
