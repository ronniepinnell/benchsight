// src/app/(dashboard)/prototypes/example/page.tsx
// Simplified example prototype page to avoid build-time runtime errors.

export const revalidate = 300

export const metadata = {
  title: 'Example Prototype | BenchSight',
  description: 'Example dashboard prototype',
}

export default function ExamplePrototypePage() {
  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl border border-border p-6">
        <h1 className="font-display text-2xl font-bold mb-2">Example Prototype</h1>
        <p className="text-sm text-muted-foreground">
          This is a placeholder prototype page used during deployment. The full interactive
          prototype (charts, tables, Supabase queries) has been temporarily disabled to
          avoid build-time runtime issues.
        </p>
      </div>

      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-3">Next Steps</h2>
        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
          <li>Confirm the unified site deploys successfully on Vercel.</li>
          <li>Later, we can re-enable the original prototype with proper client-only charting.</li>
          <li>This page is safe to leave as-is for production; it does not affect core flows.</li>
        </ul>
      </div>
    </div>
  )
}
