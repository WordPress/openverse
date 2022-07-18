import { expect, Locator } from '@playwright/test'

import {
  activeAudioStatus,
  inactiveAudioStatus,
  statusVerbMap,
  AudioStatusVerb,
} from '~/constants/audio'

const getPossibleAudioActions = async (
  context: Locator,
  options: {
    state: AudioStatusVerb[]
    filterVisible?: boolean
  }
) => {
  return (
    await Promise.all(
      options.state.map(async (s) => {
        const locator = context.locator(
          `[aria-label="${s[0].toUpperCase() + s.slice(1)}"]`
        )
        const isVisible = await locator.isVisible().catch(() => false)
        return [locator, isVisible] as const
      })
    )
  )
    .filter(options.filterVisible ? ([, visible]) => visible : (x) => x)
    .map(([l]) => l)
}

const getAllActive = async (
  context: Locator,
  options: { filterVisible?: boolean } = {}
) => {
  const locators = await getPossibleAudioActions(context, {
    ...options,
    state: activeAudioStatus.map((a) => statusVerbMap[a]),
  })
  expect(locators, 'Could not find a pause or loading button.').toHaveLength(
    options.filterVisible ? 1 : 2
  )
  return locators
}

const getActive = async (context: Locator) =>
  (await getAllActive(context, { filterVisible: true }))[0]

const getAllInactive = async (
  context: Locator,
  options: { filterVisible?: boolean } = {}
) => {
  const locators = await getPossibleAudioActions(context, {
    ...options,
    state: inactiveAudioStatus.map((a) => statusVerbMap[a]),
  })
  expect(locators, 'Could not find a play or replay button.').toHaveLength(
    options.filterVisible ? 1 : 2
  )
  return locators
}

const getInactive = async (context: Locator) =>
  (await getAllInactive(context, { filterVisible: true }))[0]

export default {
  getPossibleAudioActions,
  getAllActive,
  getActive,
  getAllInactive,
  getInactive,
}
