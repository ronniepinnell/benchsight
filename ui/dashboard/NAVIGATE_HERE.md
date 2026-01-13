# How to Navigate to Dashboard Directory

## Method 1: From Project Root (Easiest)

If you're in the project root directory (`benchsight`), just run:

```bash
cd ui/dashboard
```

## Method 2: Use the Helper Script

From the project root, run:

```bash
./go-to-dashboard.sh
```

## Method 3: Step by Step from Home

```bash
cd ~/Documents
cd "Documents - Ronnie's MacBook Pro - 1"
cd Programming_HD/Hockey/Benchsight/git/benchsight
cd ui/dashboard
```

## Method 4: Copy-Paste This Exact Command

```bash
cd ~/Documents/"Documents - Ronnie's MacBook Pro - 1"/Programming_HD/Hockey/Benchsight/git/benchsight/ui/dashboard && pwd && ls package.json
```

## Verify You're in the Right Place

After navigating, run:

```bash
pwd
ls package.json
```

You should see:
- `pwd` shows: `.../benchsight/ui/dashboard`
- `ls package.json` shows: `package.json`

## Then Run

```bash
npm install    # First time only
npm run dev    # Start the server
```
