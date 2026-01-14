'use client'

import { TeamLogo } from '@/components/teams/team-logo'
import { TrendingUp, Target, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TeamStats {
  team_id: string
  team_name: string
  team_logo?: string
  team_cd?: string
  primary_color?: string
  team_color1?: string
  team_color2?: string
  winPct?: number
  goalsFor?: number
  goalsAgainst?: number
  cfPct?: number
  ffPct?: number
  recentWinPct?: number
  homeRecord?: { wins: number; losses: number; ties: number }
  awayRecord?: { wins: number; losses: number; ties: number }
}

interface H2HStats {
  homeWins: number
  awayWins: number
  ties: number
  totalGames: number
  avgHomeGoals: number
  avgAwayGoals: number
}

interface MatchupPredictorProps {
  homeTeam: TeamStats
  awayTeam: TeamStats
  h2hHistory?: H2HStats
  isHomeGame?: boolean
}

export function MatchupPredictor({ 
  homeTeam, 
  awayTeam, 
  h2hHistory,
  isHomeGame = true 
}: MatchupPredictorProps) {
  // Calculate win probability
  const calculateWinProbability = () => {
    // Base team strength (0-1 scale)
    const homeStrength = 
      (homeTeam.winPct || 0) * 0.4 + 
      ((homeTeam.cfPct || 50) / 100) * 0.3 + 
      ((homeTeam.goalsFor || 0) / Math.max(homeTeam.goalsAgainst || 1, 1)) * 0.3
    
    const awayStrength = 
      (awayTeam.winPct || 0) * 0.4 + 
      ((awayTeam.cfPct || 50) / 100) * 0.3 + 
      ((awayTeam.goalsFor || 0) / Math.max(awayTeam.goalsAgainst || 1, 1)) * 0.3
    
    // Home ice advantage
    const homeAdvantage = 0.06
    
    // Head-to-head adjustment
    const h2hAdjustment = h2hHistory && h2hHistory.totalGames > 0
      ? ((h2hHistory.homeWins / h2hHistory.totalGames) - 0.5) * 0.1
      : 0
    
    // Recent form (last 5-10 games)
    const homeRecentForm = (homeTeam.recentWinPct || homeTeam.winPct || 0) * 0.1
    const awayRecentForm = (awayTeam.recentWinPct || awayTeam.winPct || 0) * 0.1
    
    // Calculate probabilities
    const homeWinProb = Math.max(0.1, Math.min(0.9, 
      0.5 + (homeStrength - awayStrength) + homeAdvantage + h2hAdjustment + (homeRecentForm - awayRecentForm)
    ))
    
    const awayWinProb = 1 - homeWinProb
    
    // Confidence based on data quality
    const confidence = 
      (homeTeam.winPct ? 0.3 : 0) +
      (awayTeam.winPct ? 0.3 : 0) +
      (h2hHistory && h2hHistory.totalGames > 0 ? 0.2 : 0) +
      (homeTeam.cfPct ? 0.1 : 0) +
      (awayTeam.cfPct ? 0.1 : 0)
    
    return {
      homeWinProb,
      awayWinProb,
      confidence: Math.min(1, confidence)
    }
  }
  
  const prediction = calculateWinProbability()
  const homeWinPct = Math.round(prediction.homeWinProb * 100)
  const awayWinPct = Math.round(prediction.awayWinProb * 100)
  const confidencePct = Math.round(prediction.confidence * 100)
  
  // Calculate expected goals
  const homeExpectedGoals = homeTeam.goalsFor && homeTeam.goalsAgainst
    ? ((homeTeam.goalsFor / Math.max(homeTeam.goalsAgainst, 1)) * (awayTeam.goalsAgainst || 2.5) + (homeTeam.goalsFor || 2.5)) / 2
    : null
  const awayExpectedGoals = awayTeam.goalsFor && awayTeam.goalsAgainst
    ? ((awayTeam.goalsFor / Math.max(awayTeam.goalsAgainst, 1)) * (homeTeam.goalsAgainst || 2.5) + (awayTeam.goalsFor || 2.5)) / 2
    : null
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-primary" />
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
            Matchup Prediction
          </h2>
        </div>
      </div>
      <div className="p-6 space-y-6">
        {/* Win Probability Bars */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {homeTeam.team_logo && (
                <TeamLogo
                  src={homeTeam.team_logo}
                  name={homeTeam.team_name}
                  abbrev={homeTeam.team_cd}
                  primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                  secondaryColor={homeTeam.team_color2}
                  size="xs"
                />
              )}
              <span className="text-sm font-semibold text-foreground">{homeTeam.team_name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-bold text-primary">{homeWinPct}%</span>
              <div className="w-32 h-4 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all"
                  style={{ width: `${homeWinPct}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {awayTeam.team_logo && (
                <TeamLogo
                  src={awayTeam.team_logo}
                  name={awayTeam.team_name}
                  abbrev={awayTeam.team_cd}
                  primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                  secondaryColor={awayTeam.team_color2}
                  size="xs"
                />
              )}
              <span className="text-sm font-semibold text-foreground">{awayTeam.team_name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-bold text-primary">{awayWinPct}%</span>
              <div className="w-32 h-4 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all"
                  style={{ width: `${awayWinPct}%` }}
                />
              </div>
            </div>
          </div>
        </div>
        
        {/* Key Stats Comparison */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
          <div className="space-y-2">
            <div className="text-xs font-mono text-muted-foreground uppercase">Win %</div>
            <div className="flex items-center gap-2">
              <div className="flex-1">
                <div className="text-sm font-semibold">{homeTeam.team_name}</div>
                <div className="font-mono text-lg text-primary">
                  {homeTeam.winPct ? homeTeam.winPct.toFixed(1) + '%' : '-'}
                </div>
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold">{awayTeam.team_name}</div>
                <div className="font-mono text-lg text-primary">
                  {awayTeam.winPct ? awayTeam.winPct.toFixed(1) + '%' : '-'}
                </div>
              </div>
            </div>
          </div>
          
          {(homeTeam.cfPct || awayTeam.cfPct) && (
            <div className="space-y-2">
              <div className="text-xs font-mono text-muted-foreground uppercase">CF%</div>
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <div className="text-sm font-semibold">{homeTeam.team_name}</div>
                  <div className="font-mono text-lg text-primary">
                    {homeTeam.cfPct ? homeTeam.cfPct.toFixed(1) + '%' : '-'}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold">{awayTeam.team_name}</div>
                  <div className="font-mono text-lg text-primary">
                    {awayTeam.cfPct ? awayTeam.cfPct.toFixed(1) + '%' : '-'}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {(homeTeam.goalsFor || awayTeam.goalsFor) && (
            <div className="space-y-2">
              <div className="text-xs font-mono text-muted-foreground uppercase">Goals For</div>
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <div className="text-sm font-semibold">{homeTeam.team_name}</div>
                  <div className="font-mono text-lg text-save">
                    {homeTeam.goalsFor || '-'}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold">{awayTeam.team_name}</div>
                  <div className="font-mono text-lg text-save">
                    {awayTeam.goalsFor || '-'}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {(homeTeam.goalsAgainst || awayTeam.goalsAgainst) && (
            <div className="space-y-2">
              <div className="text-xs font-mono text-muted-foreground uppercase">Goals Against</div>
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <div className="text-sm font-semibold">{homeTeam.team_name}</div>
                  <div className="font-mono text-lg text-goal">
                    {homeTeam.goalsAgainst || '-'}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold">{awayTeam.team_name}</div>
                  <div className="font-mono text-lg text-goal">
                    {awayTeam.goalsAgainst || '-'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Expected Score */}
        {(homeExpectedGoals || awayExpectedGoals) && (
          <div className="pt-4 border-t border-border">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Expected Score</div>
            <div className="flex items-center justify-center gap-4">
              <div className="text-center">
                <div className="text-xs text-muted-foreground mb-1">{homeTeam.team_name}</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {homeExpectedGoals ? homeExpectedGoals.toFixed(1) : '-'}
                </div>
              </div>
              <div className="text-muted-foreground">-</div>
              <div className="text-center">
                <div className="text-xs text-muted-foreground mb-1">{awayTeam.team_name}</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {awayExpectedGoals ? awayExpectedGoals.toFixed(1) : '-'}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Head-to-Head History */}
        {h2hHistory && h2hHistory.totalGames > 0 && (
          <div className="pt-4 border-t border-border">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Head-to-Head</div>
            <div className="text-sm text-muted-foreground">
              {homeTeam.team_name}: {h2hHistory.homeWins}W - {h2hHistory.awayWins}L
              {h2hHistory.ties > 0 && ` - ${h2hHistory.ties}T`}
              {' '}({h2hHistory.totalGames} games)
            </div>
            {h2hHistory.avgHomeGoals && h2hHistory.avgAwayGoals && (
              <div className="text-xs text-muted-foreground mt-1">
                Avg Score: {h2hHistory.avgHomeGoals.toFixed(1)} - {h2hHistory.avgAwayGoals.toFixed(1)}
              </div>
            )}
          </div>
        )}
        
        {/* Confidence Indicator */}
        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono text-muted-foreground uppercase">Prediction Confidence</div>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className={cn(
                    'h-full transition-all',
                    confidencePct >= 70 ? 'bg-save' : confidencePct >= 50 ? 'bg-primary' : 'bg-goal'
                  )}
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <span className="text-xs font-mono text-muted-foreground">{confidencePct}%</span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Based on team records, advanced stats{h2hHistory && h2hHistory.totalGames > 0 && ', and head-to-head history'}
          </div>
        </div>
      </div>
    </div>
  )
}
