# Fix GitHub Authentication Error

## The Problem
Getting "invalid username/token" error when pushing to GitHub.

## Solutions

### Option 1: Use Personal Access Token (Recommended)

**1. Create a GitHub Personal Access Token:**
- Go to: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Give it a name (e.g., "Benchsight Repo")
- Select scopes: `repo` (full control of private repositories)
- Click "Generate token"
- **Copy the token immediately** (you won't see it again!)

**2. Update your remote URL to use the token:**
```bash
# Get your current remote URL
git remote -v

# Update to use token (replace YOUR_TOKEN and YOUR_USERNAME)
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/benchsight.git

# OR use your username and token when prompted
git remote set-url origin https://github.com/YOUR_USERNAME/benchsight.git
```

**3. Push (it will prompt for password - use the token):**
```bash
git push origin --force --all
# Username: your-github-username
# Password: paste-your-token-here
```

### Option 2: Use SSH (More Secure)

**1. Check if you have SSH keys:**
```bash
ls -la ~/.ssh/id_*.pub
```

**2. If no SSH key, generate one:**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location
# Optionally set a passphrase
```

**3. Add SSH key to GitHub:**
```bash
# Copy your public key
cat ~/.ssh/id_ed25519.pub
# Copy the output
```

- Go to: https://github.com/settings/keys
- Click "New SSH key"
- Paste your public key
- Click "Add SSH key"

**4. Change remote to SSH:**
```bash
# Get your repo URL (replace with your actual username/repo)
git remote set-url origin git@github.com:YOUR_USERNAME/benchsight.git

# Test connection
ssh -T git@github.com
# Should say: "Hi YOUR_USERNAME! You've successfully authenticated..."

# Now push
git push origin --force --all
```

### Option 3: Use GitHub CLI (Easiest)

**1. Install GitHub CLI:**
```bash
brew install gh
```

**2. Authenticate:**
```bash
gh auth login
# Follow the prompts
```

**3. Push:**
```bash
git push origin --force --all
```

### Option 4: Use Credential Helper (macOS Keychain)

**1. Configure credential helper:**
```bash
git config --global credential.helper osxkeychain
```

**2. Push (will prompt once, then save to keychain):**
```bash
git push origin --force --all
# Enter username and token when prompted
# macOS will save it to keychain
```

## Quick Fix (Fastest)

**If you just need to push right now:**

1. **Get a Personal Access Token:**
   - https://github.com/settings/tokens
   - Generate new token (classic)
   - Select `repo` scope
   - Copy the token

2. **Push with token:**
```bash
git push https://YOUR_TOKEN@github.com/YOUR_USERNAME/benchsight.git --force --all
```

Replace:
- `YOUR_TOKEN` with your actual token
- `YOUR_USERNAME` with your GitHub username
- `benchsight` with your actual repo name

## Troubleshooting

**"Authentication failed"**
- Token might be expired - generate a new one
- Check token has `repo` scope
- Make sure you're using the token, not your password

**"Permission denied"**
- Make sure you have push access to the repo
- Check if repo is private and token has access

**"Repository not found"**
- Check the repo name is correct
- Verify you have access to the repo

## Recommended Setup

For long-term use, I recommend:
1. Use SSH authentication (most secure)
2. Or use GitHub CLI (easiest)
3. Or use credential helper with Personal Access Token
