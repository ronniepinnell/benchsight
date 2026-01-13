// src/app/(dashboard)/prototypes/test-connection/page.tsx
// Test page to verify Supabase connection and view available data

import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { Database, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 0 // No cache for testing

export default async function TestConnectionPage() {
  const supabase = await createClient()
  
  // Test 1: Check environment variables
  const hasUrl = !!process.env.NEXT_PUBLIC_SUPABASE_URL
  const hasKey = !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  
  // Test 2: Try to connect and query
  let connectionStatus = 'unknown'
  let errorMessage: string | null = null
  let tableCount = 0
  let sampleData: any = null
  
  try {
    // Try a simple query
    const { data, error } = await supabase
      .from('v_standings_current')
      .select('*')
      .limit(1)
    
    if (error) {
      connectionStatus = 'error'
      errorMessage = error.message
    } else {
      connectionStatus = 'success'
      sampleData = data?.[0] || null
    }
    
    // Try to get table count
    const { count } = await supabase
      .from('v_standings_current')
      .select('*', { count: 'exact', head: true })
    
    tableCount = count || 0
  } catch (err: any) {
    connectionStatus = 'error'
    errorMessage = err.message || 'Unknown error'
  }

  return (
    <PrototypeTemplate 
      title="Supabase Connection Test" 
      description="Verify your Supabase connection and view available data"
    >
      {/* Environment Variables Check */}
      <div className="bg-card rounded-xl border border-border p-6 space-y-4">
        <h2 className="font-display text-lg font-semibold flex items-center gap-2">
          <Database className="w-5 h-5" />
          Environment Variables
        </h2>
        
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            {hasUrl ? (
              <CheckCircle className="w-4 h-4 text-save" />
            ) : (
              <XCircle className="w-4 h-4 text-goal" />
            )}
            <span className="text-sm">
              NEXT_PUBLIC_SUPABASE_URL: {hasUrl ? '✅ Set' : '❌ Missing'}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {hasKey ? (
              <CheckCircle className="w-4 h-4 text-save" />
            ) : (
              <XCircle className="w-4 h-4 text-goal" />
            )}
            <span className="text-sm">
              NEXT_PUBLIC_SUPABASE_ANON_KEY: {hasKey ? '✅ Set' : '❌ Missing'}
            </span>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className={cn(
        "bg-card rounded-xl border p-6",
        connectionStatus === 'success' ? 'border-save' : 'border-goal'
      )}>
        <h2 className="font-display text-lg font-semibold flex items-center gap-2 mb-4">
          {connectionStatus === 'success' ? (
            <>
              <CheckCircle className="w-5 h-5 text-save" />
              Connection Successful
            </>
          ) : (
            <>
              <XCircle className="w-5 h-5 text-goal" />
              Connection Failed
            </>
          )}
        </h2>
        
        {connectionStatus === 'success' ? (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              ✅ Successfully connected to Supabase!
            </p>
            <p className="text-sm text-muted-foreground">
              Found {tableCount} teams in standings
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-goal font-semibold">
              ❌ Failed to connect to Supabase
            </p>
            {errorMessage && (
              <div className="bg-muted rounded p-3 mt-2">
                <p className="text-xs font-mono text-foreground">{errorMessage}</p>
              </div>
            )}
            <div className="mt-4 space-y-1 text-sm text-muted-foreground">
              <p>To fix:</p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Create <code className="bg-muted px-1 rounded">.env.local</code> in <code className="bg-muted px-1 rounded">ui/dashboard/</code></li>
                <li>Add your Supabase URL and anon key</li>
                <li>Restart the dev server</li>
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Sample Data */}
      {sampleData && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Sample Data</h2>
          <div className="bg-muted rounded p-4">
            <pre className="text-xs overflow-auto">
              {JSON.stringify(sampleData, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Available Views Info */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Available Data Views
        </h2>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>If connection is successful, you can query these views:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><code className="bg-muted px-1 rounded">v_standings_current</code> - Current standings</li>
            <li><code className="bg-muted px-1 rounded">v_leaderboard_points</code> - Points leaders</li>
            <li><code className="bg-muted px-1 rounded">v_leaderboard_goals</code> - Goals leaders</li>
            <li><code className="bg-muted px-1 rounded">v_player_season_stats</code> - Player stats</li>
            <li><code className="bg-muted px-1 rounded">v_team_season_stats</code> - Team stats</li>
            <li><code className="bg-muted px-1 rounded">v_game_summary</code> - Game summaries</li>
          </ul>
        </div>
      </div>
    </PrototypeTemplate>
  )
}
