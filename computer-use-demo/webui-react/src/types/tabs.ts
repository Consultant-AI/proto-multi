export type TabType = 'newtab' | 'files' | 'web' | 'terminal' | 'computer' | 'computers'

export interface Tab {
  id: string
  type: TabType
  title: string
  icon?: string | JSX.Element // Custom icon (emoji, favicon URL, or JSX element)
  resourceId?: string // ID of the resource (file path, URL, etc.)
}
