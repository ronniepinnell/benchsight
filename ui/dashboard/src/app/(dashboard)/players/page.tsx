// src/app/(dashboard)/players/page.tsx
import Link from 'next/link'
import { getCurrentRankings } from '@/lib/supabase/queries/players'
import { Search, TrendingUp, Target, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Players | BenchSight',
  description: 'NORAD Hockey League player statistics',
}

export default async function PlayersPage() {
  const players = await getCurrentRankings(50)
  
  // Get leaders for quick stats
  const pointsLeader = players[0]
  const goalsLeader = [...players].sort((a, b) => b.goals - a.goals)[0]
  const assistsLeader = [...players].sort((a, b) => b.assists - a.assists)[0]
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Player Rankings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Current season player statistics and rankings
        </p>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link 
          href="/leaders?tab=points"
          className="bg-card rounded-lg p-4 border border-border hover:border-primary/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Points Leader</span>
          </div>
          {pointsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                {pointsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-primary">{pointsLeader.points} pts</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/leaders?tab=goals"
          className="bg-card rounded-lg p-4 border border-border hover:border-goal/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-goal" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Goals Leader</span>
          </div>
          {goalsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-goal transition-colors">
                {goalsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-goal">{goalsLeader.goals} G</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/leaders?tab=assists"
          className="bg-card rounded-lg p-4 border border-border hover:border-assist/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-assist" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Assists Leader</span>
          </div>
          {assistsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-assist transition-colors">
                {assistsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-assist">{assistsLeader.assists} A</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/players/compare"
          className="bg-card rounded-lg p-4 border border-border hover:border-shot/50 transition-colors flex flex-col justify-center items-center"
        >
          <Search className="w-8 h-8 text-shot mb-2" />
          <span className="font-display text-sm font-semibold text-foreground">Compare Players</span>
          <span className="text-xs text-muted-foreground">Side-by-side stats</span>
        </Link>
      </div>
      
      {/* Players Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-accent border-b-2 border-border">
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider w-16">
                  Rank
                </th>
                <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Player
                </th>
                <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Team
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  GP
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider">
                  G
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider">
                  A
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider">
                  P
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  P/G
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  PIM
                </th>
              </tr>
            </thead>
            <tbody>
              {players.map((player) => {
                const isTop3 = player.points_rank <= 3
                
                return (
                  <tr
                    key={player.player_id}
                    className={cn(
                      'border-b border-border transition-colors hover:bg-muted/50',
                      player.points_rank % 2 === 0 && 'bg-accent/30'
                    )}
                  >
                    <td className="px-4 py-3 text-center">
                      <span className={cn(
                        'font-display font-bold',
                        isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                      )}>
                        {player.points_rank}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {player.player_id ? (
                        <Link
                          href={`/players/${player.player_id}`}
                          className="font-display text-sm text-foreground hover:text-primary transition-colors"
                        >
                          {player.player_name}
                        </Link>
                      ) : (
                        <span className="font-display text-sm text-foreground">
                          {player.player_name}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {player.team_name ? (
                        <Link href={`/team/${player.team_name.replace(/\s+/g, '_')}`} className="hover:text-foreground transition-colors">
                          {player.team_name}
                        </Link>
                      ) : (
                        <span>{player.team_name || '-'}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                      {player.games_played}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-goal font-semibold">
                      {player.goals}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-assist">
                      {player.assists}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-xl font-bold text-primary">
                      {player.points}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                      {player.points_per_game?.toFixed(2) ?? '-'}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                      {player.pim}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
