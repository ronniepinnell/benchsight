/**
 * Admin Portal Page
 * 
 * Embedded admin portal for ETL control and system management
 * 
 * Note: The portal is a standalone HTML/JS application that can be:
 * 1. Embedded as an iframe (current approach)
 * 2. Converted to React components (future enhancement)
 */

'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function AdminPortalPage() {
  const [apiUrl, setApiUrl] = useState<string>('http://localhost:8000')
  const [supabaseUrl, setSupabaseUrl] = useState<string>('')
  const [supabaseKey, setSupabaseKey] = useState<string>('')
  const [showInfo, setShowInfo] = useState(true)

  useEffect(() => {
    // Get environment variables
    const apiUrlEnv = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const supabaseUrlEnv = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
    const supabaseKeyEnv = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

    setApiUrl(apiUrlEnv)
    setSupabaseUrl(supabaseUrlEnv)
    setSupabaseKey(supabaseKeyEnv)
  }, [])

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      {showInfo && (
        <div className="p-4 bg-card border rounded-lg relative">
          <button
            onClick={() => setShowInfo(false)}
            className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
          >
            ×
          </button>
          <h2 className="text-lg font-semibold mb-2">Admin Portal</h2>
          <p className="text-sm text-muted-foreground mb-3">
            Manage ETL jobs, view system status, and browse data. The portal connects to the ETL API backend.
          </p>
          <div className="text-xs text-muted-foreground space-y-1 mb-3">
            <div>API URL: <code className="bg-muted px-1 py-0.5 rounded">{apiUrl}</code></div>
            <div>Supabase: <code className="bg-muted px-1 py-0.5 rounded">{supabaseUrl ? 'Connected' : 'Not configured'}</code></div>
          </div>
          <div className="flex gap-2">
            <Link href="/norad/tracker">
              <Button variant="outline" size="sm">Open Tracker</Button>
            </Link>
            <Link href="/norad/standings">
              <Button variant="outline" size="sm">View Dashboard</Button>
            </Link>
          </div>
        </div>
      )}

      {/* Embedded Portal */}
      <div className="border rounded-lg overflow-hidden" style={{ height: 'calc(100vh - 12rem)' }}>
        <iframe
          src="/portal/index.html"
          className="w-full h-full"
          title="Admin Portal"
          style={{ border: 'none' }}
        />
      </div>

      {/* Setup Instructions */}
      <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-lg">
        <p className="mb-2">
          <strong>Setup:</strong> To enable the portal, copy portal files to the public directory:
        </p>
        <code className="block bg-background px-2 py-1 rounded mb-2 text-xs">
          ./scripts/setup-portal.sh
        </code>
        <p className="mt-2">
          The portal requires the ETL API to be running at <code className="bg-background px-1 py-0.5 rounded">{apiUrl}</code>
        </p>
      </div>
    </div>
  )
}
