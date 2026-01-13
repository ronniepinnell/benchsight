// src/components/prototypes/design-system.tsx
// Design system reference component - shows all available colors, typography, spacing

import { PrototypeTemplate } from './prototype-template'
import { Target, Trophy, Save, Zap, AlertTriangle, Users } from 'lucide-react'

export function DesignSystemReference() {
  return (
    <PrototypeTemplate 
      title="Design System Reference" 
      description="Quick reference for colors, typography, and components"
    >
      {/* Colors */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">Hockey Colors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <div className="bg-goal/20 border border-goal rounded p-3">
              <div className="text-goal font-mono font-semibold">text-goal</div>
              <div className="text-xs text-muted-foreground mt-1">Goals, losses, negative</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="bg-assist/20 border border-assist rounded p-3">
              <div className="text-assist font-mono font-semibold">text-assist</div>
              <div className="text-xs text-muted-foreground mt-1">Assists, positive metrics</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="bg-save/20 border border-save rounded p-3">
              <div className="text-save font-mono font-semibold">text-save</div>
              <div className="text-xs text-muted-foreground mt-1">Saves, wins, positive</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="bg-shot/20 border border-shot rounded p-3">
              <div className="text-shot font-mono font-semibold">text-shot</div>
              <div className="text-xs text-muted-foreground mt-1">Shots, attempts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Typography */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">Typography</h2>
        <div className="space-y-4">
          <div>
            <div className="text-xs text-muted-foreground mb-1">Display Font (Headings)</div>
            <div className="font-display text-2xl font-bold">Rajdhani Bold 2xl</div>
            <div className="font-display text-xl font-semibold">Rajdhani Semibold xl</div>
            <div className="font-display text-lg">Rajdhani Regular lg</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">Mono Font (Stats)</div>
            <div className="font-mono text-2xl font-bold">JetBrains Mono 2xl</div>
            <div className="font-mono text-lg">JetBrains Mono lg</div>
            <div className="font-mono text-sm">JetBrains Mono sm</div>
          </div>
        </div>
      </div>

      {/* Spacing */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">Spacing</h2>
        <div className="space-y-2 text-sm">
          <div><code className="bg-muted px-2 py-1 rounded">space-y-6</code> - Vertical spacing between sections</div>
          <div><code className="bg-muted px-2 py-1 rounded">gap-4</code> - Grid gaps</div>
          <div><code className="bg-muted px-2 py-1 rounded">p-6</code> - Card padding</div>
          <div><code className="bg-muted px-2 py-1 rounded">p-4</code> - Smaller padding</div>
        </div>
      </div>

      {/* Component Examples */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">Component Examples</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-goal" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">42</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Points</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">128</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Save className="w-4 h-4 text-save" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Saves</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">95%</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">12</div>
          </div>
        </div>
      </div>
    </PrototypeTemplate>
  )
}
