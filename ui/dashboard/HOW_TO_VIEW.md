# How to View Dashboard Pages

## ✅ Quick Answer

**Yes, the dashboard reads data directly from Supabase!**

## Steps to View Pages

### 1. Set Up Environment (One Time)

```bash
cd ui/dashboard

# Create .env.local file
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
EOF
```

**Get your credentials from:**
- Supabase Dashboard → Settings → API
- Copy "Project URL" and "anon/public key"

### 2. Install & Start

```bash
# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

### 3. Open in Browser

Visit: **http://localhost:3000**

**Key Pages:**
- `/prototypes/test-connection` - Test Supabase connection
- `/prototypes/example` - Example prototype with data
- `/standings` - League standings
- `/leaders` - Scoring leaders

## How Data Reading Works

The dashboard reads **directly from Supabase** using:

```tsx
import { createClient } from '@/lib/supabase/server'

export default async function MyPage() {
  const supabase = await createClient()
  
  // Read from Supabase
  const { data } = await supabase
    .from('v_standings_current')
    .select('*')
  
  return <div>{/* Use data here */}</div>
}
```

## Test Your Connection

1. Start dev server: `npm run dev`
2. Visit: http://localhost:3000/prototypes/test-connection
3. This page will show:
   - ✅ Environment variables status
   - ✅ Connection status
   - ✅ Sample data if connected
   - ❌ Error messages if not connected

## Troubleshooting

**"Missing environment variables"**
→ Create `.env.local` in `ui/dashboard/`

**"Cannot connect"**
→ Check Supabase URL and key are correct

**"Table does not exist"**
→ Run ETL and upload: `python run_etl.py && python upload.py`
