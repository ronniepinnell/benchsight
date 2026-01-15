// src/components/goalies/goalie-tabs/saves-tab-wrapper.tsx
import { SavesTab } from './saves-tab'

interface SavesTabWrapperProps {
  goalieId: string
}

export async function SavesTabWrapper({ goalieId }: SavesTabWrapperProps) {
  return <SavesTab goalieId={goalieId} />
}
