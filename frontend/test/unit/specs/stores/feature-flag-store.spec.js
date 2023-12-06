import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { useFeatureFlagStore, getFlagStatus } from "~/stores/feature-flag"
import { OFF, COOKIE, SESSION } from "~/constants/feature-flag"

jest.mock(
  "~~/feat/feature-flags.json",
  () => ({
    features: {
      feat_enabled: {
        status: "enabled",
        description: "Will always be enabled",
        storage: "cookie",
      },
      feat_disabled: {
        status: "disabled",
        description: "Will always be disabled",
        storage: "cookie",
      },
      feat_switchable_optout: {
        status: "switchable",
        description: "Can be switched between on and off",
        defaultState: "on",
        storage: "cookie",
      },
      feat_switchable_optin: {
        status: "switchable",
        description: "Can be switched between on and off",
        defaultState: "off",
        storage: "session",
      },
      feat_no_query: {
        status: "switchable",
        description: "Cannot be flipped by ff_ query params",
        defaultState: "off",
        supportsQuery: false,
      },
      feat_env_specific: {
        status: {
          local: "enabled",
          staging: "switchable",
          production: "disabled",
        },
        description: "Depends on the environment",
        defaultState: "off",
        storage: "cookie",
      },
    },
  }),
  { virtual: true }
)

describe("Feature flag store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("initialises state from JSON", () => {
    const featureFlagStore = useFeatureFlagStore()
    expect(Object.keys(featureFlagStore.flags).length).toBe(6)
  })

  it.each`
    flagName           | featureState
    ${"feat_enabled"}  | ${"on"}
    ${"feat_disabled"} | ${"off"}
  `(
    "does not allow modification of fixed flags",
    ({ flagName, featureState }) => {
      const featureFlagStore = useFeatureFlagStore()
      expect(featureFlagStore.featureState(flagName)).toEqual(featureState)
      expect(featureFlagStore.isOn(flagName)).toEqual(featureState === "on")
    }
  )

  it.each`
    doCookieInit | featureState
    ${false}     | ${"on"}
    ${true}      | ${"off"}
  `(
    "cascades cookie-storage flag from cookies",
    ({ doCookieInit, featureState }) => {
      const flagName = "feat_switchable_optout"
      const featureFlagStore = useFeatureFlagStore()
      if (doCookieInit)
        {featureFlagStore.initFromCookies({
          feat_switchable_optout: OFF,
        })}
      expect(featureFlagStore.featureState(flagName)).toEqual(featureState)
      expect(featureFlagStore.isOn(flagName)).toEqual(featureState === "on")
    }
  )

  it.each`
    cookieState | queryState | finalState
    ${"off"}    | ${"on"}    | ${"on"}
    ${"on"}     | ${"off"}   | ${"off"}
  `(
    "cascades flag from cookies and query params",
    ({ cookieState, queryState, finalState }) => {
      const flagName = "feat_switchable_optout"
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.initFromCookies({
        [flagName]: cookieState,
      })
      featureFlagStore.initFromQuery({
        [`ff_${flagName}`]: queryState,
      })

      expect(featureFlagStore.featureState(flagName)).toEqual(finalState)
    }
  )

  it.each`
    flagName           | queryState | finalState
    ${"feat_disabled"} | ${"on"}    | ${"off"}
    ${"feat_enabled"}  | ${"off"}   | ${"on"}
  `(
    "does not cascade non-switchable flags from query params",
    ({ flagName, queryState, finalState }) => {
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.initFromQuery({
        [`ff_${flagName}`]: queryState,
      })

      expect(featureFlagStore.featureState(flagName)).toEqual(finalState)
    }
  )

  it("does not cascade query-unsupporting flags from query params", () => {
    const featureFlagStore = useFeatureFlagStore()
    expect(featureFlagStore.featureState("feat_no_query")).toEqual(OFF)
    featureFlagStore.initFromQuery({
      feat_no_query: "on",
    })
    expect(featureFlagStore.featureState("feat_no_query")).toEqual(OFF)
  })

  it.each`
    environment     | featureState
    ${"local"}      | ${"on"}
    ${"staging"}    | ${"off"}
    ${"production"} | ${"off"}
  `(
    "returns $expectedState for $environment",
    ({ environment, featureState }) => {
      // Back up value of `DEPLOYMENT_ENV` and replace it
      const old_env = process.env.DEPLOYMENT_ENV
      process.env.DEPLOYMENT_ENV = environment

      const featureFlagStore = useFeatureFlagStore()
      expect(featureFlagStore.featureState("feat_env_specific")).toEqual(
        featureState
      )
      expect(featureFlagStore.isOn("feat_env_specific")).toEqual(
        featureState === "on"
      )

      // Restore `DEPLOYMENT_ENV` value
      process.env.DEPLOYMENT_ENV = old_env
    }
  )

  it.each`
    environment     | flagStatus
    ${"local"}      | ${"switchable"}
    ${"staging"}    | ${"switchable"}
    ${"production"} | ${"disabled"}
  `(
    "handles fallback for missing $environment",
    ({ environment, flagStatus }) => {
      // Back up value of `DEPLOYMENT_ENV` and replace it
      const old_env = process.env.DEPLOYMENT_ENV
      process.env.DEPLOYMENT_ENV = environment

      expect(getFlagStatus({ status: { staging: "switchable" } })).toEqual(
        flagStatus
      )

      // Restore `DEPLOYMENT_ENV` value
      process.env.DEPLOYMENT_ENV = old_env
    }
  )

  it.each`
    storage    | flagName
    ${COOKIE}  | ${"feat_switchable_optout"}
    ${SESSION} | ${"feat_switchable_optin"}
  `("returns mapping of switchable flags", ({ storage, flagName }) => {
    const featureFlagStore = useFeatureFlagStore()
    const flagStateMap = featureFlagStore.flagStateMap(storage)

    expect(flagStateMap).toHaveProperty(flagName)

    expect(flagStateMap).not.toHaveProperty("feat_enabled")
    expect(flagStateMap).not.toHaveProperty("feat_disabled")
  })
})
