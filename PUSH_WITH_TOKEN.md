# Push to GitHub with Personal Access Token

## The Problem
Git is still asking for a password even when using token in URL.

## Solution: Use Token in URL Correctly

### Option 1: Use the Script (Easiest)

```bash
# Get your token from: https://github.com/settings/tokens
./scripts/push_with_token.sh YOUR_TOKEN_HERE
```

### Option 2: Manual Push with Token

**Method A: Set remote URL with token (temporary)**
```bash
# Set remote with token
git remote set-url origin https://YOUR_TOKEN@github.com/ronniepinnell/benchsight.git

# Push
git push origin --force --all

# Reset remote (optional, for security)
git remote set-url origin https://github.com/ronniepinnell/benchsight.git
```

**Method B: Use token in push command**
```bash
# Push directly with token in URL
git push https://YOUR_TOKEN@github.com/ronniepinnell/benchsight.git --force --all
```

**Method C: Use GIT_ASKPASS (most secure)**
```bash
# Set token as environment variable
export GIT_ASKPASS=echo
export GIT_PASSWORD=YOUR_TOKEN

# Or create a simple script
echo '#!/bin/sh
exec echo "$GIT_PASSWORD"' > /tmp/git-askpass.sh
chmod +x /tmp/git-askpass.sh
export GIT_ASKPASS=/tmp/git-askpass.sh
export GIT_PASSWORD=YOUR_TOKEN

# Now push
git push origin --force --all
```

### Option 3: Use Credential Helper (Saves Token)

```bash
# Configure credential helper
git config credential.helper osxkeychain

# Push (will prompt once, then save)
git push origin --force --all

# When prompted:
# Username: ronniepinnell
# Password: [paste your token]
```

macOS will save it to keychain for future use.

### Option 4: Switch to SSH (Best Long-term)

```bash
# 1. Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# 2. If no key, generate one
ssh-keygen -t ed25519 -C "ronnie.pinnell@gmail.com"
# Press Enter to accept defaults

# 3. Copy public key
cat ~/.ssh/id_ed25519.pub
# Copy the output

# 4. Add to GitHub:
#    - Go to: https://github.com/settings/keys
#    - Click "New SSH key"
#    - Paste your public key
#    - Save

# 5. Change remote to SSH
git remote set-url origin git@github.com:ronniepinnell/benchsight.git

# 6. Test connection
ssh -T git@github.com
# Should say: "Hi ronniepinnell! You've successfully authenticated..."

# 7. Push
git push origin --force --all
```

## Troubleshooting

**Still asking for password?**
- Make sure token is correct (no extra spaces)
- Token must have `repo` scope
- Try using the script: `./scripts/push_with_token.sh YOUR_TOKEN`

**"Authentication failed"**
- Token might be expired - generate a new one
- Check token has `repo` scope enabled
- Verify you have push access to the repo

**"Repository not found"**
- Check repo name is correct: `ronniepinnell/benchsight`
- Verify you have access to the repository

## Recommended: Use SSH

SSH is the most secure and doesn't require tokens. Once set up, you never need to enter credentials again.
