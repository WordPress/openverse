import { useCookie } from "#imports"

import { defineStore } from "pinia"
import { useStorage } from "@vueuse/core"

import featureData from "~~/feat/feature-flags.json"

import { warn } from "~/utils/console"

import type { FeatureFlag } from "~/types/feature-flag"
import {
  FeatureState,
  FlagStatus,
  ENABLED,
  SWITCHABLE,
  ON,
  OFF,
  DISABLED,
  COOKIE,
  SESSION,
} from "~/constants/feature-flag"
import { LOCAL, DEPLOY_ENVS, DeployEnv } from "~/constants/deploy-env"

import type { OpenverseCookieState } from "~/types/cookies"

import type { LocationQuery, LocationQueryValue } from "vue-router"

type FlagName = keyof (typeof featureData)["features"]

export const isFlagName = (name: string): name is FlagName => {
  return Object.keys(featureData.features).includes(name)
}
export interface FeatureFlagState {
  flags: Record<FlagName, FeatureFlag>
}

const FEATURE_FLAG = "feature_flag"

/**
 * Get the status of the flag. If the flag status is environment dependent, this
 * function will use the flag status for the current environment based on the
 * `DEPLOYMENT_ENV` environment variable.
 *
 * @param flag - the flag for which to get the status
 */
export const getFlagStatus = (flag: FeatureFlag): FlagStatus => {
  const deployEnv = (process.env.DEPLOYMENT_ENV ?? LOCAL) as DeployEnv
  if (typeof flag.status === "string") {
    return flag.status
  } else {
    const envIndex = DEPLOY_ENVS.indexOf(deployEnv)
    for (let i = envIndex; i < DEPLOY_ENVS.length; i += 1) {
      if (DEPLOY_ENVS[i] in flag.status) {
        return flag.status[DEPLOY_ENVS[i]]
      }
    }
  }
  return DISABLED
}

/**
 * Get the state of the feature based on the status of the feature flag and the
 * preferences of the user.
 *
 * @param flag - the flag for which to get the state
 */
const getFeatureState = (flag: FeatureFlag): FeatureState => {
  const status = getFlagStatus(flag)
  if (status === SWITCHABLE) {
    return flag.preferredState ?? flag.defaultState ?? OFF
  }
  if (status === ENABLED) {
    return ON
  }
  return OFF
}

export const useFeatureFlagStore = defineStore(FEATURE_FLAG, {
  state: () =>
    ({
      flags: featureData.features,
    } as FeatureFlagState),
  getters: {
    /**
     * Get the state of the named feature, based on config and cookie.
     *
     * Prefer `isOn` for most use cases.
     */
    featureState:
      (state: FeatureFlagState) =>
      (name: FlagName): FeatureState => {
        if (name in state.flags) {
          return getFeatureState(state.flags[name])
        } else {
          warn(`Invalid feature flag accessed: ${name}`)
          return ON
        }
      },
    /**
     * Proxy for `featureState` to simplify the majority of flag state checks.
     *
     * Prefer this for most use cases over using `featureState` directly.
     *
     * @returns `true` if the flag is on, false otherwise
     */
    isOn() {
      return (name: FlagName): boolean => this.featureState(name) === ON
    },
    /**
     * Get the mapping of switchable features to their preferred states.
     */
    flagStateMap:
      (state: FeatureFlagState) =>
      (dest: string): Record<string, FeatureState> => {
        const featureMap: Record<string, FeatureState> = {}
        Object.entries(state.flags).forEach(([name, flag]) => {
          if (getFlagStatus(flag) === SWITCHABLE && flag.storage === dest) {
            featureMap[name] = getFeatureState(flag)
          }
        })
        return featureMap
      },
  },
  actions: {
    /**
     * Given a list of key value pairs of flags and their preferred states,
     * populate the store state to match the cookie. The cookie may be
     * persistent, if written by `writeToCookie`, or session-scoped, if written
     * by `writeToSession`.
     *
     * @param cookies - mapping of feature flags and their preferred states
     */
    initFromCookies(cookies: Record<string, FeatureState>) {
      Object.entries(cookies).forEach(([name, state]) => {
        const flag = this.flags[name as FlagName]
        if (flag && getFlagStatus(flag) === SWITCHABLE) {
          flag.preferredState = state
        }
      })
    },
    /**
     * Write the current state of the feature flags to the cookie. These cookies
     * are read in the corresponding `initFromCookies` method.
     */
    writeToCookie() {
      const featuresCookie =
        useCookie<OpenverseCookieState["features"]>("features")
      featuresCookie.value = this.flagStateMap(COOKIE)
    },
    /**
     * Write the current state of the switchable flags to the session cookie.
     * These cookies are read in the corresponding `initFromCookies` method.
     *
     * This is same as `writeToCookie`, except these cookies are not persistent
     * and will be deleted by the browser after the session.
     */
    writeToSession() {
      const sessionFeaturesCookie =
        useCookie<OpenverseCookieState["sessionFeatures"]>("sessionFeatures")
      sessionFeaturesCookie.value = this.flagStateMap(SESSION)
    },
    /**
     * Set the value of flag entries from the query parameters. Only those
     * query parameters that contain the 'ff_' prefix are considered.
     *
     * Values set using query params are per-session, and will not affect the
     * value stored in the cookie.
     *
     * @param query - values for the feature flags
     */
    initFromQuery(query: LocationQuery) {
      const isValidName = (name: string): name is `ff_${FlagName}` =>
        name.startsWith("ff_") && name.replace("ff_", "") in this.flags
      const isValidValue = (
        value: string | (string | null)[] | LocationQueryValue
      ): value is FeatureState =>
        typeof value === "string" && ["on", "off"].includes(value)
      const isValidEntry = (
        entry: [string, string | (string | null)[] | LocationQueryValue]
      ): entry is [`ff_${FlagName}`, FeatureState] =>
        isValidName(entry[0]) && isValidValue(entry[1])

      Object.entries(query)
        .filter(isValidEntry)
        .forEach(([name, state]) => {
          // TODO: type `FlagName` should be inferred by TS
          const flagName = name.substring(3) as FlagName
          const flag = this.flags[flagName]
          if (
            getFlagStatus(flag) === SWITCHABLE &&
            flag.supportsQuery !== false
          ) {
            flag.preferredState = state
          }
        })
    },
    /**
     * Toggle the feature flag of the given name to the given preferred state.
     *
     * @param name - the name of the flag to toggle
     * @param targetState - the desired state of the feature flag
     */
    toggleFeature(name: FlagName, targetState: FeatureState) {
      const flag = this.flags[name]
      if (getFlagStatus(flag) === SWITCHABLE) {
        flag.preferredState = targetState
        this.writeToCookie()
        this.writeToSession()
        if (name === "analytics") {
          this.syncAnalyticsWithLocalStorage()
        }
      } else {
        warn(`Cannot set preferred state for non-switchable flag: ${name}`)
      }
    },
    /**
     * For Plausible to stop tracking `plausible_ignore` must be set in
     * `localStorage`.
     * @see {@link https://plausible.io/docs/excluding-localstorage}
     */
    syncAnalyticsWithLocalStorage() {
      const storage = useStorage<boolean | null>("plausible_ignore", null)
      storage.value =
        getFeatureState(this.flags["analytics"]) === ON ? null : true
    },
  },
})
