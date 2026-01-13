# Installing Node.js and npm

You need Node.js installed to run the dashboard. Node.js includes npm (Node Package Manager).

## Quick Install (Recommended)

### Option 1: Using Homebrew (Easiest)

If you have Homebrew installed:

```bash
brew install node
```

Then verify:
```bash
node --version
npm --version
```

### Option 2: Download from Website

1. Go to: https://nodejs.org
2. Download the **LTS version** (Long Term Support)
3. Run the installer
4. Restart your terminal
5. Verify:
   ```bash
   node --version
   npm --version
   ```

### Option 3: Using nvm (Node Version Manager)

If you want to manage multiple Node versions:

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal, then:
nvm install --lts
nvm use --lts
```

## After Installation

1. **Close and reopen your terminal** (important!)
2. Verify installation:
   ```bash
   node --version   # Should show v18.x.x or higher
   npm --version    # Should show 9.x.x or higher
   ```

3. Navigate to dashboard:
   ```bash
   cd ui/dashboard
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

5. Start dev server:
   ```bash
   npm run dev
   ```

## Troubleshooting

### "Command not found" after installing

- **Close and reopen Terminal** - This is the most common issue!
- Or run: `source ~/.zshrc` (if using zsh)

### Still not working?

Check if Node.js is in your PATH:
```bash
which node
which npm
```

If nothing shows, you may need to add Node.js to your PATH manually.

### Check if Homebrew is installed

```bash
brew --version
```

If Homebrew is not installed, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
