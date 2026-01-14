# Quick Fix: GitHub Authentication Error

## The Problem
GitHub no longer accepts passwords for HTTPS. You need a **Personal Access Token**.

## Quick Solution (3 Steps)

### Step 1: Create Personal Access Token

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token (classic)"**
3. Name it: `Benchsight Repo`
4. Select scope: **`repo`** (full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Clear Old Credentials

```bash
# Remove old GitHub password from keychain
security delete-internet-password -s github.com
```

### Step 3: Push with Token

```bash
# Push (will prompt for credentials)
git push origin --force --all

# When prompted:
# Username: ronniepinnell
# Password: [paste your Personal Access Token here]
```

macOS will save the token to your keychain for future use.

## Alternative: Use SSH (More Secure)

**1. Generate SSH key (if you don't have one):**
```bash
ssh-keygen -t ed25519 -C "ronnie.pinnell@gmail.com"
# Press Enter to accept defaults
```

**2. Add SSH key to GitHub:**
```bash
# Copy your public key
cat ~/.ssh/id_ed25519.pub
# Copy the output
```

- Go to: https://github.com/settings/keys
- Click "New SSH key"
- Paste your public key
- Click "Add SSH key"

**3. Change remote to SSH:**
```bash
git remote set-url origin git@github.com:ronniepinnell/benchsight.git
```

**4. Test and push:**
```bash
ssh -T git@github.com
git push origin --force --all
```

## Or Use GitHub CLI (Easiest)

```bash
# Install
brew install gh

# Login
gh auth login

# Push
git push origin --force --all
```

## Quick One-Liner (If You Have Token)

```bash
# Replace YOUR_TOKEN with your actual token
git push https://YOUR_TOKEN@github.com/ronniepinnell/benchsight.git --force --all
```

## Your Current Setup

- **Remote:** `https://github.com/ronniepinnell/benchsight.git`
- **Username:** `ronniepinnell`
- **Credential Helper:** macOS Keychain (already configured)

Just need to update with a Personal Access Token!
