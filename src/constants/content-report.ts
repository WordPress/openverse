export const DMCA = 'dmca'
export const MATURE = 'mature'
export const OTHER = 'other'

export const reasons = [DMCA, MATURE, OTHER] as const

export type ReportReason = typeof reasons[number]

export const SENT = 'sent'
export const FAILED = 'failed'
export const WIP = 'wip'

export const statuses = [SENT, FAILED, WIP] as const

export type ReportStatus = typeof statuses[number]

export const DMCA_FORM_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLSd0I8GsEbGQLdaX4K_F6V2NbHZqN137WMZgnptUpzwd-kbDKA/viewform'
