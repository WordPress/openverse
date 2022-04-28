export const audioLayouts = ['full', 'box', 'row', 'global'] as const
export const audioSizes = ['s', 'm', 'l'] as const
export const audioStatuses = ['playing', 'paused', 'played'] as const
export const audioFeatures = ['timestamps', 'duration', 'seek'] as const

export type AudioLayout = typeof audioLayouts[number]
export type AudioSize = typeof audioSizes[number]
export type AudioStatus = typeof audioStatuses[number]
export type AudioFeature = typeof audioFeatures[number]

export const layoutMappings = {
  full: 'VFullLayout',
  row: 'VRowLayout',
  box: 'VBoxLayout',
  global: 'VGlobalLayout',
}
