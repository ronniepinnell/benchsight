import { TrendingUp, Target, Sparkles, Shield } from 'lucide-react'
import { CollapsibleSection } from '@/components/common/collapsible-section'
import { cn, formatSeason } from '@/lib/utils'
import Link from 'next/link'

interface CareerTabProps {
  playerId: string
  career: any
  playerPosition?: string
  hasPlayedGoalie?: boolean
  hasPlayedSkater?: boolean
  isBoth?: boolean
  seasonStatsForCareer?: any[]
  goalieSeasonStatsForCareer?: any[]
  regularSeasonStats?: any[]
  playoffSeasonStats?: any[]
}

export function CareerTab({ 
  playerId, 
  career, 
  playerPosition, 
  hasPlayedGoalie = false,
  hasPlayedSkater = true,
  isBoth = false,
  seasonStatsForCareer = [], 
  goalieSeasonStatsForCareer = [],
  regularSeasonStats = [],
  playoffSeasonStats = []
}: CareerTabProps) {
  const seasonStats = seasonStatsForCareer
  const goalieSeasonStats = goalieSeasonStatsForCareer
  
  // Calculate career totals from season stats if career summary is missing
  let careerTotals = career
  if (!careerTotals && seasonStats && seasonStats.length > 0) {
    const totals = seasonStats.reduce((acc, stat) => ({
      total_games: acc.total_games + (Number(stat.games_played) || 0),
      total_goals: acc.total_goals + (Number(stat.goals) || 0),
      total_assists: acc.total_assists + (Number(stat.assists) || 0),
      total_points: acc.total_points + (Number(stat.points) || 0),
      total_pim: acc.total_pim + (Number(stat.pim) || 0),
    }), { total_games: 0, total_goals: 0, total_assists: 0, total_points: 0, total_pim: 0 })
    
    careerTotals = {
      ...totals,
      goals_per_game: totals.total_games > 0 ? (totals.total_goals / totals.total_games) : 0,
      assists_per_game: totals.total_games > 0 ? (totals.total_assists / totals.total_games) : 0,
      points_per_game: totals.total_games > 0 ? (totals.total_points / totals.total_games) : 0,
    }
  }
  
  // For goalies, calculate career totals
  let goalieCareerTotals: any = null
  let careerGAA: number | null = null
  let careerSV: number | null = null
  if (hasPlayedGoalie && goalieSeasonStats.length > 0) {
    goalieCareerTotals = goalieSeasonStats.reduce((acc, stat) => ({
      total_games: acc.total_games + (Number(stat.games_played) || 0),
      total_goals_against: acc.total_goals_against + (Number(stat.goals_against) || 0),
      total_saves: acc.total_saves + (Number(stat.saves) || 0),
      total_shots_against: acc.total_shots_against + (Number(stat.shots_against) || 0),
    }), { total_games: 0, total_goals_against: 0, total_saves: 0, total_shots_against: 0 })
    
    if (goalieCareerTotals.total_games > 0) {
      careerGAA = goalieCareerTotals.total_goals_against / goalieCareerTotals.total_games
    }
    if (goalieCareerTotals.total_shots_against > 0) {
      careerSV = (goalieCareerTotals.total_saves / goalieCareerTotals.total_shots_against) * 100
    }
  }
  
  // Merge season stats with goalie stats for year-by-year
  const yearByYearStats = (seasonStats || []).map(stat => {
    const goalieStat = goalieSeasonStats.find(g => g.season_id === stat.season_id)
    return {
      ...stat,
      gaa: goalieStat?.gaa || null,
      goals_against: goalieStat?.goals_against || null,
      save_percent: goalieStat?.save_percent || goalieStat?.sv_pct || null,
      avg_rating: stat.avg_rating || null,
    }
  })
  
  // Also create year-by-year goalie stats
  const yearByYearGoalieStats = goalieSeasonStats.map(stat => ({
    ...stat,
    team_name: stat.team_name || null,
  }))
  
  if (!careerTotals && (!seasonStats || seasonStats.length === 0) && (!hasPlayedGoalie || goalieSeasonStats.length === 0)) {
    return (
      <div className="bg-card rounded-xl border border-border p-6 text-center">
        <p className="text-sm text-muted-foreground">No career data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Skater Career Totals */}
      {hasPlayedSkater && (
        <CollapsibleSection
          title={isBoth ? "Career Totals - Skater" : "Career Totals"}
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {careerTotals?.total_games || careerTotals?.career_games || careerTotals?.games_played || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Target className="w-3 h-3 text-goal" />
                  <span className="text-xs font-mono text-goal uppercase">G</span>
                </div>
                <div className="font-mono text-2xl font-bold text-goal">
                  {careerTotals?.total_goals || careerTotals?.career_goals || careerTotals?.goals || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Sparkles className="w-3 h-3 text-assist" />
                  <span className="text-xs font-mono text-assist uppercase">A</span>
                </div>
                <div className="font-mono text-2xl font-bold text-assist">
                  {careerTotals?.total_assists || careerTotals?.career_assists || careerTotals?.assists || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="w-3 h-3 text-primary" />
                  <span className="text-xs font-mono text-primary uppercase">PTS</span>
                </div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {careerTotals?.total_points || careerTotals?.career_points || careerTotals?.points || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">PIM</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {careerTotals?.total_pim || careerTotals?.career_pim || careerTotals?.pim || 0}
                </div>
              </div>
            </div>
            
            {/* Career Averages */}
            <div className="mt-6 pt-6 border-t border-border">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Averages</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">G/GP</div>
                  <div className="font-mono text-xl font-bold text-foreground">
                    {careerTotals?.goals_per_game 
                      ? Number(careerTotals.goals_per_game).toFixed(2)
                      : (careerTotals?.total_games || careerTotals?.career_games || 0) > 0
                        ? ((careerTotals?.total_goals || careerTotals?.career_goals || 0) / (careerTotals?.total_games || careerTotals?.career_games || 1)).toFixed(2)
                        : '0.00'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">A/GP</div>
                  <div className="font-mono text-xl font-bold text-foreground">
                    {careerTotals?.assists_per_game
                      ? Number(careerTotals.assists_per_game).toFixed(2)
                      : (careerTotals?.total_games || careerTotals?.career_games || 0) > 0
                        ? ((careerTotals?.total_assists || careerTotals?.career_assists || 0) / (careerTotals?.total_games || careerTotals?.career_games || 1)).toFixed(2)
                        : '0.00'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">PTS/GP</div>
                  <div className="font-mono text-xl font-bold text-primary">
                    {careerTotals?.points_per_game
                      ? Number(careerTotals.points_per_game).toFixed(2)
                      : (careerTotals?.total_games || careerTotals?.career_games || 0) > 0
                        ? ((careerTotals?.total_points || careerTotals?.career_points || 0) / (careerTotals?.total_games || careerTotals?.career_games || 1)).toFixed(2)
                        : '0.00'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Goalie Career Totals */}
      {hasPlayedGoalie && goalieCareerTotals && (
        <CollapsibleSection
          title={isBoth ? "Career Totals - Goalie" : "Career Totals"}
          icon={<Shield className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {goalieCareerTotals.total_games || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Shield className="w-3 h-3 text-primary" />
                  <span className="text-xs font-mono text-primary uppercase">GAA</span>
                </div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {careerGAA ? careerGAA.toFixed(2) : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">SV%</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {careerSV ? careerSV.toFixed(1) + '%' : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Saves</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {goalieCareerTotals.total_saves || 0}
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Year-by-Year Breakdown - Skater */}
      {hasPlayedSkater && yearByYearStats.length > 0 && (
        <CollapsibleSection
          title={isBoth ? "Year-by-Year Stats - Skater" : "Year-by-Year Stats"}
          icon={<Target className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Season</th>
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                  <th colSpan={3} className="px-2 py-2 text-center font-display text-xs text-muted-foreground border-l border-border">Regular Season</th>
                  <th colSpan={3} className="px-2 py-2 text-center font-display text-xs text-muted-foreground border-l border-border">Playoffs</th>
                  <th colSpan={4} className="px-2 py-2 text-center font-display text-xs text-muted-foreground border-l border-border">Totals</th>
                </tr>
                <tr className="border-b border-border bg-accent/30">
                  <th></th>
                  <th></th>
                  <th></th>
                  <th className="px-2 py-1 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-primary">PTS</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-primary">PTS</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-1 text-center font-display text-xs text-primary">PTS</th>
                </tr>
              </thead>
              <tbody>
                {yearByYearStats.map((stat, index) => {
                  const seasonId = stat.season_id
                  const regularStat = regularSeasonStats.find(s => s.season_id === seasonId)
                  const playoffStat = playoffSeasonStats.find(s => s.season_id === seasonId)
                  
                  const totalGP = Number(stat.games_played) || 0
                  const totalGoals = Number(stat.goals) || 0
                  const totalAssists = Number(stat.assists) || 0
                  const totalPoints = Number(stat.points) || 0
                  
                  const regularGP = Number(regularStat?.games_played) || 0
                  const regularGoals = Number(regularStat?.goals) || 0
                  const regularPoints = Number(regularStat?.points) || 0
                  
                  const playoffGP = Number(playoffStat?.games_played) || 0
                  const playoffGoals = Number(playoffStat?.goals) || 0
                  const playoffPoints = Number(playoffStat?.points) || 0
                  
                  const avgRating = stat.avg_rating ? Number(stat.avg_rating) : null
                  
                  return (
                    <tr key={stat.season_id || `season-${index}`} className="border-b border-border hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-xs text-foreground font-semibold">
                        {formatSeason(stat.season || stat.season_id)}
                      </td>
                      <td className="px-4 py-2">
                        {stat.team_name ? (
                          <Link
                            href={`/norad/team/${(stat.team_name || '').replace(/\s+/g, '_')}`}
                            className="text-sm text-foreground hover:text-primary transition-colors font-display"
                          >
                            {stat.team_name}
                          </Link>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {avgRating != null ? avgRating.toFixed(1) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-foreground border-l border-border">{regularGP || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{regularGoals || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary">{regularPoints || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-foreground border-l border-border">{playoffGP || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{playoffGoals || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary">{playoffPoints || '-'}</td>
                      <td className="px-2 py-2 text-center font-mono text-foreground font-semibold border-l border-border">{totalGP}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{totalGoals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{totalAssists}</td>
                      <td className="px-2 py-2 text-center font-mono font-bold text-primary">{totalPoints}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Year-by-Year Breakdown - Goalie */}
      {hasPlayedGoalie && yearByYearGoalieStats.length > 0 && (
        <CollapsibleSection
          title={isBoth ? "Year-by-Year Stats - Goalie" : "Year-by-Year Stats"}
          icon={<Shield className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Season</th>
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">GAA</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">SV%</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Wins</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Losses</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shutouts</th>
                </tr>
              </thead>
              <tbody>
                {yearByYearGoalieStats.map((stat, index) => {
                  const gp = Number(stat.games_played) || 0
                  
                  return (
                    <tr key={stat.season_id || `goalie-season-${index}`} className="border-b border-border hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-xs text-foreground font-semibold">
                        {formatSeason(stat.season || stat.season_id)}
                      </td>
                      <td className="px-4 py-2">
                        {stat.team_name ? (
                          <Link
                            href={`/norad/team/${(stat.team_name || '').replace(/\s+/g, '_')}`}
                            className="text-sm text-foreground hover:text-primary transition-colors font-display"
                          >
                            {stat.team_name}
                          </Link>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-foreground">{gp}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                        {stat.gaa ? Number(stat.gaa).toFixed(2) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {stat.save_percent 
                          ? Number(stat.save_percent).toFixed(1) + '%'
                          : stat.sv_pct
                            ? Number(stat.sv_pct).toFixed(1) + '%'
                            : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {stat.wins || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {stat.losses || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {stat.shutouts || 0}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CollapsibleSection>
      )}
    </div>
  )
}
