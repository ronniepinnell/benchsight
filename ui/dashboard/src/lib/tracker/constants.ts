/**
 * Tracker Constants and Reference Data
 * Extracted from tracker_index_v23.5.html LISTS object
 */

import type { EventType } from './types'

export const EVENT_TYPES: EventType[] = [
  'Faceoff',
  'Shot',
  'Pass',
  'Goal',
  'Turnover',
  'Zone_Entry_Exit',
  'Penalty',
  'Stoppage',
  'Possession',
  'Save',
  'Rebound',
  'DeadIce',
  'Play',
  'Intermission',
  'Clockstop',
  'Timeout'
]

export const EVENT_HOTKEYS: Record<EventType, string> = {
  Faceoff: 'F',
  Shot: 'S',
  Pass: 'P',
  Goal: 'G',
  Turnover: 'T',
  Zone_Entry_Exit: 'Z',
  Penalty: 'N',
  Stoppage: 'X',
  Possession: 'O',
  Save: 'V',
  Rebound: 'R',
  DeadIce: 'D',
  Play: 'Y',
  Intermission: 'I',
  Clockstop: 'C',
  Timeout: 'T' // Note: Conflicts with Turnover, but this is from original
}

export interface EventDetails {
  d1: string[]
  d2?: string[]
  d2_Giveaway?: string[]
  d2_Takeaway?: string[]
  d2_Entry?: string[]
  d2_Exit?: string[]
  d2_Offensive?: string[]
  d2_Defensive?: string[]
  d2_Play?: string[]
}

export const EVENT_DETAILS: Record<EventType, EventDetails> = {
  Shot: {
    d1: ['Shot_OnNetSaved', 'Shot_Missed', 'Shot_Blocked', 'Shot_BlockedSameTeam', 'Shot_Deflected', 'Shot_OnNetGoal'],
    d2: ['Shot-Wrist', 'Shot-Slap', 'Shot-Backhand', 'Shot-Snap', 'Shot-WrapAround', 'Shot-Bat', 'Shot-Poke', 'Shot-OneTime', 'Shot-Tip', 'Shot-Deflection', 'Shot-Other']
  },
  Pass: {
    d1: ['Pass_Completed', 'Pass_Missed', 'Pass_Deflected', 'Pass_Intercepted'],
    d2: ['Pass-Stretch', 'Pass-Rim/Wrap', 'Pass-Backhand', 'Pass-Forehand', 'Pass-Bank', 'Pass-Dump', 'Pass-Drop', 'Pass-OneTouch', 'Pass-Other']
  },
  Goal: {
    d1: ['Goal_Scored', 'Goal_Shootout', 'Goal_PenaltyShot'],
    d2: ['Goal-Wrist', 'Goal-Slap', 'Goal-Backhand', 'Goal-Tip', 'Goal-Snap', 'Goal-WrapAround', 'Goal-Deflection', 'Goal-OneTime', 'Goal-Other']
  },
  Faceoff: {
    d1: ['Faceoff_PeriodStart', 'Faceoff_GameStart', 'Faceoff_AfterGoal', 'Faceoff_AfterPenalty', 'Faceoff_AfterStoppage'],
    d2: []
  },
  Turnover: {
    d1: ['Turnover_Giveaway', 'Turnover_Takeaway'],
    d2_Giveaway: ['Giveaway-Misplayed', 'Giveaway-BattleLost', 'Giveaway-PassIntercepted', 'Giveaway-Other'],
    d2_Takeaway: ['Takeaway-BattleWon', 'Takeaway-PokeCheck', 'Takeaway-PassIntercepted', 'Takeaway-Other']
  },
  Zone_Entry_Exit: {
    d1: ['Zone_Entry', 'Zone_Exit', 'Zone_Keepin', 'Zone_EntryFailed', 'Zone_ExitFailed'],
    d2_Entry: ['ZoneEntry-Rush', 'ZoneEntry-Pass', 'ZoneEntry-DumpIn', 'ZoneEntry-Chip'],
    d2_Exit: ['ZoneExit-Rush', 'ZoneExit-Pass', 'ZoneExit-Clear', 'ZoneExit-Chip']
  },
  Save: {
    d1: ['Save_Rebound', 'Save_Freeze', 'Save_Played'],
    d2: ['Save-Glove', 'Save-Blocker', 'Save-Pad', 'Save-Stick', 'Save-Butterfly', 'Save-Other']
  },
  Stoppage: {
    d1: ['Stoppage_PeriodEnd', 'Stoppage_Play', 'Stoppage_Other', 'Stoppage_GameEnd'],
    d2_Play: ['Stoppage-Icing', 'Stoppage-Offsides', 'Stoppage-GoalieStoppage', 'Stoppage-PuckOut', 'Stoppage-Penalty', 'Stoppage-Goal']
  },
  Penalty: {
    d1: ['Penalty_Minor', 'Penalty_Major', 'Penalty_Misconduct'],
    d2: ['Penalty-Tripping', 'Penalty-Hooking', 'Penalty-Slashing', 'Penalty-Interference', 'Penalty-Holding', 'Penalty-Roughing', 'Penalty-HighSticking', 'Penalty-CrossChecking', 'Penalty-Boarding', 'Penalty-Other']
  },
  Possession: {
    d1: ['Breakaway', 'PuckRetrieval', 'PuckRecovery', 'Regroup', 'LoosePuck'],
    d2: []
  },
  Rebound: {
    d1: ['Rebound_TeamRecovered', 'Rebound_OppRecovered', 'Rebound_ShotGenerated'],
    d2: []
  },
  DeadIce: {
    d1: ['DeadIce_Icing', 'DeadIce_Offside', 'DeadIce_PuckOut', 'DeadIce_NetOff', 'DeadIce_Other'],
    d2: []
  },
  Play: {
    d1: ['Play_Offensive', 'Play_Defensive'],
    d2_Offensive: ['Play-DriveMiddle', 'Play-DriveWide', 'Play-CrashNet', 'Play-Deke', 'Play-DumpChase', 'Play-Forecheck'],
    d2_Defensive: ['Play-PokeCheck', 'Play-Backcheck', 'Play-Contain', 'Play-BoxOut']
  },
  Intermission: {
    d1: ['Intermission_Period1', 'Intermission_Period2', 'Intermission_Period3', 'Intermission_OT'],
    d2: []
  },
  Clockstop: {
    d1: ['Clockstop_Injury', 'Clockstop_Equipment', 'Clockstop_IceRepair', 'Clockstop_Other'],
    d2: []
  },
  Timeout: {
    d1: ['Timeout_Home', 'Timeout_Away'],
    d2: []
  }
}

export const SHIFT_START_TYPES = [
  'GameStart',
  'PeriodStart',
  'FaceoffAfterGoal',
  'FaceoffAfterPenalty',
  'OtherFaceoff',
  'Stoppage',
  'Intermission',
  'OnTheFly'
]

export const SHIFT_STOP_TYPES = [
  '',
  'OnTheFly',
  'PeriodEnd',
  'Period End',
  'GoalScored',
  'Home Goal',
  'Away Goal',
  'Penalty',
  'Stoppage',
  'OtherFaceoff',
  'Intermission',
  'GameEnd',
  'High Stick',
  'Away Icing',
  'Home Icing',
  'Away Offside',
  'Home Offside',
  'Puck Out of Play',
  'Away Goalie Stopped (after Home SOG)',
  'Home Goalie Stopped (after Away SOG)'
]

export const SHIFT_TYPES = {
  start: SHIFT_START_TYPES,
  stop: SHIFT_STOP_TYPES
}

export const MAIN_EVENT_TYPES: EventType[] = [
  'Faceoff',
  'Shot',
  'Pass',
  'Goal',
  'Turnover',
  'Zone_Entry_Exit',
  'Stoppage',
  'Penalty',
  'Possession',
  'Save',
  'Rebound',
  'Play'
]

export const EVENT_TYPE_COLORS: Record<EventType, string> = {
  Goal: '#22c55e',
  Shot: '#3b82f6',
  Penalty: '#ef4444',
  Turnover: '#f59e0b',
  Faceoff: '#64748b',
  Pass: '#8b5cf6',
  Zone_Entry_Exit: '#06b6d4',
  Stoppage: '#94a3b8',
  Possession: '#10b981',
  Save: '#14b8a6',
  Rebound: '#f97316',
  DeadIce: '#6b7280',
  Play: '#6366f1',
  Intermission: '#9ca3af',
  Clockstop: '#a1a1aa',
  Timeout: '#d4d4d8'
}
