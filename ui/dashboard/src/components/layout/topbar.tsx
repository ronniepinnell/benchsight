// src/components/layout/topbar.tsx
export function Topbar() {
  return (
    <header className="fixed top-0 left-60 right-0 h-14 bg-card border-b border-border flex items-center justify-between px-6 z-40">
      {/* Left side - Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-save/10 border border-save/50 rounded-md">
          <div className="w-2 h-2 rounded-full bg-save animate-pulse" />
          <span className="text-[10px] font-mono text-save tracking-wider">
            SYSTEM ONLINE
          </span>
        </div>
        
        <span className="text-xs font-mono text-muted-foreground">
          2025-26 Season • Week 18
        </span>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        <span className="text-xs font-mono text-muted-foreground">
          NORAD HOCKEY ANALYTICS
        </span>
      </div>
    </header>
  )
}
