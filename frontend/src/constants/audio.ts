export type AudioLayout = (typeof audioLayouts)[number]
export const audioLayouts = Object.freeze([
  "full",
  "box",
  "row",
  "global",
] as const)

export type AudioSize = (typeof audioSizes)[number]
export const audioSizes = Object.freeze(["s", "m", "l"] as const)

export type AudioStatus = (typeof audioStatuses)[number]
export const audioStatuses = Object.freeze([
  "playing",
  "paused",
  "played",
  "loading",
] as const)

export type AudioFeature = (typeof audioFeatures)[number]
export const audioFeatures = Object.freeze([
  "timestamps",
  "duration",
  "seek",
] as const)

export const inactiveAudioStatus: readonly AudioStatus[] = Object.freeze([
  "paused",
  "played",
])
export const activeAudioStatus: readonly AudioStatus[] = Object.freeze([
  "playing",
  "loading",
])

export const layoutMappings = Object.freeze({
  full: "VFullLayout",
  row: "VRowLayout",
  box: "VBoxLayout",
  global: "VGlobalLayout",
})

export const statusVerbMap = Object.freeze({
  playing: "pause",
  paused: "play",
  played: "replay",
  loading: "loading",
} as const)

export const audioStatusVerbs = Object.values(statusVerbMap)
export type AudioStatusVerb = (typeof audioStatusVerbs)[number]
export const audioErrorMessages = {
  NotAllowedError: "err_unallowed",
  NotSupportedError: "err_unsupported",
  AbortError: "err_aborted",
} as const
