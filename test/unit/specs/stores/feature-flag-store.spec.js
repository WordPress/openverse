import { setActivePinia, createPinia } from 'pinia'

import { useFeatureFlagStore, getFlagStatus } from '~/stores/feature-flag'
import { OFF, ON } from '~/constants/feature-flag'

jest.mock(
  '~~/feat/feature-flags.json',
  () => ({
    features: {
      feat_enabled: {
        status: 'enabled',
        description: 'Will always be enabled',
      },
      feat_disabled: {
        status: 'disabled',
        description: 'Will always be disabled',
      },
      feat_switchable_optout: {
        status: 'switchable',
        description: 'Can be switched between on and off',
        defaultState: 'on',
      },
      feat_switchable_optin: {
        status: 'switchable',
        description: 'Can be switched between on and off',
        defaultState: 'off',
      },
      feat_env_specific: {
        status: {
          local: 'enabled',
          staging: 'switchable',
          production: 'disabled',
        },
        description: 'Depends on the environment',
        defaultState: 'off',
      },
    },
  }),
  { virtual: true }
)

describe('Feature flag store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initialises state from JSON', () => {
    const featureFlagStore = useFeatureFlagStore()
    expect(Object.keys(featureFlagStore.flags).length).toBe(5)
  })

  it.each`
    flagName           | featureState
    ${'feat_enabled'}  | ${'on'}
    ${'feat_disabled'} | ${'off'}
  `(
    'does not allow modification of fixed flags',
    ({ flagName, featureState }) => {
      const featureFlagStore = useFeatureFlagStore()
      expect(featureFlagStore.featureState(flagName)).toEqual(featureState)
    }
  )

  it.each`
    flagName                    | doCookieInit | featureState
    ${'feat_switchable_optout'} | ${false}     | ${'on'}
    ${'feat_switchable_optin'}  | ${false}     | ${'off'}
    ${'feat_switchable_optout'} | ${true}      | ${'off'}
    ${'feat_switchable_optin'}  | ${true}      | ${'on'}
  `(
    'cascades flag $flagName from cookies',
    ({ flagName, doCookieInit, featureState }) => {
      const featureFlagStore = useFeatureFlagStore()
      if (doCookieInit)
        featureFlagStore.initFromCookies({
          feat_switchable_optout: OFF,
          feat_switchable_optin: ON,
        })
      expect(featureFlagStore.featureState(flagName)).toEqual(featureState)
    }
  )

  it.each`
    environment     | featureState
    ${'local'}      | ${'on'}
    ${'staging'}    | ${'off'}
    ${'production'} | ${'off'}
  `(
    'returns $expectedState for $environment',
    ({ environment, featureState }) => {
      // Back up value of `DEPLOYMENT_ENV` and replace it
      const old_env = process.env.DEPLOYMENT_ENV
      process.env.DEPLOYMENT_ENV = environment

      const featureFlagStore = useFeatureFlagStore()
      expect(featureFlagStore.featureState('feat_env_specific')).toEqual(
        featureState
      )

      // Restore `DEPLOYMENT_ENV` value
      process.env.DEPLOYMENT_ENV = old_env
    }
  )

  it.each`
    environment     | flagStatus
    ${'local'}      | ${'switchable'}
    ${'staging'}    | ${'switchable'}
    ${'production'} | ${'disabled'}
  `(
    'handles fallback for missing $environment',
    ({ environment, flagStatus }) => {
      // Back up value of `DEPLOYMENT_ENV` and replace it
      const old_env = process.env.DEPLOYMENT_ENV
      process.env.DEPLOYMENT_ENV = environment

      expect(getFlagStatus({ status: { staging: 'switchable' } })).toEqual(
        flagStatus
      )

      // Restore `DEPLOYMENT_ENV` value
      process.env.DEPLOYMENT_ENV = old_env
    }
  )

  it('returns mapping of switchable flags', () => {
    const featureFlagStore = useFeatureFlagStore()
    const flagStateMap = featureFlagStore.flagStateMap

    expect(flagStateMap).toHaveProperty('feat_switchable_optout')
    expect(flagStateMap).toHaveProperty('feat_switchable_optin')

    expect(flagStateMap).not.toHaveProperty('feat_enabled')
    expect(flagStateMap).not.toHaveProperty('feat_disabled')
  })
})
