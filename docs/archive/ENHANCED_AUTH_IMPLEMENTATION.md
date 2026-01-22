# Enhanced Authentication Implementation Plan

**Complete guide to implementing advanced authentication features**

Last Updated: 2026-01-21

---

## Current State

✅ **Basic Auth:** Supabase Auth with email/password  
✅ **Protected Routes:** Middleware protecting `/admin` and `/tracker`  
✅ **User Menu:** Basic user display and logout

---

## Phase 1: Role-Based Access Control (RBAC)

### 1.1 Database Schema

```sql
-- User roles table
CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  league_id UUID REFERENCES leagues(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- 'super_admin', 'league_admin', 'team_manager', etc.
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, league_id, team_id)
);

-- Permissions table
CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role TEXT NOT NULL,
  resource TEXT NOT NULL, -- 'games', 'players', 'teams', 'admin'
  action TEXT NOT NULL,   -- 'read', 'write', 'delete', 'manage'
  scope TEXT NOT NULL,    -- 'all', 'league', 'team', 'own'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default permissions
INSERT INTO permissions (role, resource, action, scope) VALUES
  ('super_admin', '*', '*', '*'),
  ('league_admin', 'games', '*', 'league'),
  ('league_admin', 'teams', '*', 'league'),
  ('league_admin', 'users', 'read', 'league'),
  ('team_manager', 'games', 'write', 'team'),
  ('team_manager', 'players', 'read', 'team'),
  ('scorer', 'games', 'write', 'assigned'),
  ('scorer', 'games', 'read', 'team'),
  ('coach', 'analytics', 'read', 'team'),
  ('coach', 'games', 'read', 'team'),
  ('player', 'stats', 'read', 'own');
```

### 1.2 Permission Check Function

```typescript
// lib/auth/permissions.ts
export async function hasPermission(
  userId: string,
  resource: string,
  action: string,
  scope?: string
): Promise<boolean> {
  const supabase = createClient();
  
  // Get user roles
  const { data: roles } = await supabase
    .from('user_roles')
    .select('role, league_id, team_id')
    .eq('user_id', userId);
  
  if (!roles || roles.length === 0) return false;
  
  // Check each role for permission
  for (const userRole of roles) {
    const { data: permission } = await supabase
      .from('permissions')
      .select('*')
      .eq('role', userRole.role)
      .eq('resource', resource)
      .eq('action', action)
      .single();
    
    if (permission) {
      // Check scope
      if (permission.scope === '*') return true;
      if (permission.scope === scope) return true;
      if (permission.scope === 'all') return true;
    }
  }
  
  return false;
}
```

### 1.3 Middleware Enhancement

```typescript
// middleware.ts (enhanced)
export async function middleware(request: NextRequest) {
  // ... existing auth check ...
  
  // Check permissions for protected routes
  if (isProtectedRoute && user) {
    const resource = getResourceFromPath(request.nextUrl.pathname);
    const action = getActionFromMethod(request.method);
    
    const hasAccess = await hasPermission(
      user.id,
      resource,
      action
    );
    
    if (!hasAccess) {
      return NextResponse.redirect(
        new URL('/unauthorized', request.url)
      );
    }
  }
  
  return response;
}
```

---

## Phase 2: Team & League Management

### 2.1 Database Schema

```sql
-- Leagues table
CREATE TABLE leagues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Teams table
CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  league_id UUID REFERENCES leagues(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  abbreviation TEXT,
  logo_url TEXT,
  colors JSONB, -- {primary: '#000000', secondary: '#FFFFFF'}
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User-League associations
CREATE TABLE user_leagues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  league_id UUID REFERENCES leagues(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, league_id)
);

-- User-Team associations
CREATE TABLE user_teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, team_id)
);
```

### 2.2 League Management UI

```typescript
// app/(dashboard)/admin/leagues/page.tsx
export default function LeaguesPage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  
  return (
    <div>
      <h1>League Management</h1>
      <Button onClick={createLeague}>Create League</Button>
      
      <Table>
        {leagues.map(league => (
          <LeagueRow key={league.id} league={league} />
        ))}
      </Table>
    </div>
  );
}
```

---

## Phase 3: OAuth & SSO

### 3.1 Google OAuth Setup

1. **Create Google OAuth App**
   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Add redirect URI: `https://your-app.vercel.app/auth/callback`

2. **Configure Supabase**
   ```typescript
   // Enable Google provider in Supabase Dashboard
   // Add client ID and secret
   ```

3. **Frontend Integration**
   ```typescript
   // components/auth/login-button.tsx
   export function GoogleLoginButton() {
     const handleGoogleLogin = async () => {
       const { data, error } = await supabase.auth.signInWithOAuth({
         provider: 'google',
         options: {
           redirectTo: `${window.location.origin}/auth/callback`
         }
       });
     };
     
     return (
       <Button onClick={handleGoogleLogin}>
         <GoogleIcon /> Sign in with Google
       </Button>
     );
   }
   ```

---

## Phase 4: Two-Factor Authentication

### 4.1 TOTP Setup

```typescript
// lib/auth/2fa.ts
import { authenticator } from 'otplib';

export async function enable2FA(userId: string) {
  // Generate secret
  const secret = authenticator.generateSecret();
  
  // Generate QR code
  const serviceName = 'BenchSight';
  const accountName = user.email;
  const otpAuthUrl = authenticator.keyuri(
    accountName,
    serviceName,
    secret
  );
  
  // Save secret (encrypted) to database
  await supabase
    .from('user_2fa')
    .upsert({
      user_id: userId,
      secret: encrypt(secret),
      enabled: false // Enable after verification
    });
  
  return { secret, qrCode: generateQRCode(otpAuthUrl) };
}

export async function verify2FA(userId: string, token: string) {
  const { data } = await supabase
    .from('user_2fa')
    .select('secret')
    .eq('user_id', userId)
    .single();
  
  const secret = decrypt(data.secret);
  const isValid = authenticator.verify({ token, secret });
  
  return isValid;
}
```

### 4.2 2FA UI

```typescript
// app/(dashboard)/settings/security/page.tsx
export default function SecuritySettings() {
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [qrCode, setQrCode] = useState<string | null>(null);
  
  const enable2FA = async () => {
    const { secret, qrCode } = await enable2FA(user.id);
    setQrCode(qrCode);
    // Show QR code for user to scan
  };
  
  return (
    <div>
      <h2>Two-Factor Authentication</h2>
      {!twoFactorEnabled ? (
        <Button onClick={enable2FA}>Enable 2FA</Button>
      ) : (
        <Button onClick={disable2FA}>Disable 2FA</Button>
      )}
      {qrCode && <QRCodeDisplay code={qrCode} />}
    </div>
  );
}
```

---

## Phase 5: Session Management

### 5.1 Active Sessions Display

```typescript
// app/(dashboard)/settings/sessions/page.tsx
export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  
  useEffect(() => {
    loadSessions();
  }, []);
  
  const loadSessions = async () => {
    const { data } = await supabase
      .from('user_sessions')
      .select('*')
      .eq('user_id', user.id)
      .order('last_activity', { ascending: false });
    
    setSessions(data);
  };
  
  const revokeSession = async (sessionId: string) => {
    await supabase
      .from('user_sessions')
      .delete()
      .eq('id', sessionId);
    
    loadSessions();
  };
  
  return (
    <div>
      <h2>Active Sessions</h2>
      {sessions.map(session => (
        <SessionCard
          key={session.id}
          session={session}
          onRevoke={() => revokeSession(session.id)}
        />
      ))}
    </div>
  );
}
```

---

## Implementation Checklist

### Week 1: RBAC Foundation
- [ ] Create database schema
- [ ] Implement permission checking
- [ ] Update middleware
- [ ] Test permission system

### Week 2: Team/League Management
- [ ] Create database tables
- [ ] Build league management UI
- [ ] Build team management UI
- [ ] Implement user assignment

### Week 3: OAuth Integration
- [ ] Set up Google OAuth
- [ ] Add OAuth buttons
- [ ] Test OAuth flow
- [ ] Add other providers (optional)

### Week 4: 2FA & Sessions
- [ ] Implement TOTP
- [ ] Build 2FA UI
- [ ] Implement session management
- [ ] Test security features

---

## Next Steps

1. **Start with RBAC** (most critical)
2. **Add team/league management** (enables multi-tenancy)
3. **Add OAuth** (improves UX)
4. **Add 2FA** (enhances security)

---

*See `docs/COMPREHENSIVE_FUTURE_ROADMAP.md` for full roadmap*
