import { useCookie, useRuntimeConfig } from "#imports"

import { defineStore } from "pinia"
import { useStorage } from "@vueuse/core"

import featureData from "~~/feat/feature-flags.json"

import { warn } from "~/utils/console"

import type {
  FeatureFlag,
  FeatureFlagRecord,
  FlagName,
} from "~/types/feature-flag"
import {
  COOKIE,
  DISABLED,
  ENABLED,
  FeatureState,
  FLAG_STATUSES,
  FlagStatus,
  OFF,
  ON,
  SESSION,
  SWITCHABLE,
} from "~/constants/feature-flag"
import { DEPLOY_ENVS, DeployEnv } from "~/constants/deploy-env"

import {
  OpenverseCookieState,
  persistentCookieOptions,
  sessionCookieOptions,
} from "~/types/cookies"

import type { LocationQuery, LocationQueryValue } from "vue-router"

export const isFlagName = (name: string): name is FlagName => {
  return Object.keys(featureData.features).includes(name)
}
export interface FeatureFlagState {
  flags: Record<FlagName, FeatureFlag>
}

interface FeatureGroup {
  title: string
  features: FeatureFlag[]
}

/**
 * Get the status of the flag. If the flag status is environment dependent, this
 * function will use the flag status for the current environment based on the
 * value from the runtime config.
 *
 * @param flag - the flag for which to get the status
 * @param deploymentEnv - the current deployment environment
 */
export const getFlagStatus = (
  flag: FeatureFlagRecord,
  deploymentEnv: DeployEnv
): FlagStatus => {
  if (typeof flag.status === "string") {
    if (!FLAG_STATUSES.includes(flag.status as FlagStatus)) {
      warn(`Invalid ${flag.description} flag status: ${flag.status}`)
      return DISABLED
    }
    return flag.status as FlagStatus
  } else {
    const envIndex = DEPLOY_ENVS.indexOf(deploymentEnv)
    for (let i = envIndex; i < DEPLOY_ENVS.length; i += 1) {
      if (DEPLOY_ENVS[i] in flag.status) {
        if (
          !FLAG_STATUSES.includes(flag.status[DEPLOY_ENVS[i]] as FlagStatus)
        ) {
          warn(
            `Invalid ${flag.description} flag status: ${flag.status[DEPLOY_ENVS[i]]}`
          )
          return DISABLED
        }
        return flag.status[DEPLOY_ENVS[i]] as FlagStatus
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
 * @param deploymentEnv - the current deployment environment
 */
const getFeatureState = (
  flag: FeatureFlag | FeatureFlagRecord,
  deploymentEnv: DeployEnv
): FeatureState => {
  const status = getFlagStatus(flag, deploymentEnv)
  if (status === SWITCHABLE) {
    if ("preferredState" in flag) {
      return (flag.preferredState as FeatureState) ?? flag.defaultState ?? OFF
    }
    return flag.defaultState ?? OFF
  }
  if (status === ENABLED) {
    return ON
  }
  return OFF
}

export const initializeFlagState = (deploymentEnv: DeployEnv) => {
  // Resolve the status of the feature flags based on the current environment
  const features: Record<FlagName, FeatureFlag> = Object.entries(
    featureData.features as Record<FlagName, FeatureFlagRecord>
  ).reduce(
    (acc, [name, flag]) => {
      acc[name as FlagName] = {
        ...flag,
        name: name as FlagName,
        state: getFeatureState(flag, deploymentEnv),
        status: getFlagStatus(flag, deploymentEnv),
        preferredState: undefined,
      }
      return acc
    },
    {} as Record<FlagName, FeatureFlag>
  )
  return { flags: features, groups: featureData.groups }
}

const FEATURE_FLAG = "feature_flag"

export const useFeatureFlagStore = defineStore(FEATURE_FLAG, {
  state: () => {
    const deploymentEnv = useRuntimeConfig().public.deploymentEnv as DeployEnv
    return initializeFlagState(deploymentEnv)
  },
  getters: {
    /**
     * Get the state of the named feature, based on config and cookie.
     *
     * Prefer `isOn` for most use cases.
     */
    featureState:
      (state: FeatureFlagState) =>
      (name: FlagName): FeatureState => {
        if (!isFlagName(name)) {
          warn(`Invalid feature flag accessed: ${name}`)
          return ON
        }
        return state.flags[name].state
      },

    /**
     * Get the mapping of switchable features to their preferred states.
     */
    flagStateMap:
      (state: FeatureFlagState) =>
      (dest: string): Record<string, FeatureState> => {
        const featureMap: Record<string, FeatureState> = {}
        Object.entries(state.flags).forEach(([name, flag]) => {
          if (
            flag.status === SWITCHABLE &&
            flag.preferredState !== undefined &&
            flag.storage === dest
          ) {
            featureMap[name] = flag.state
          }
        })
        return featureMap
      },
  },
  actions: {
    getFlagsBySwitchable(switchable: boolean): FeatureFlag[] {
      return Object.entries(this.flags)
        .filter((feature) => (feature[1].status === SWITCHABLE) === switchable)
        .map((feature) => feature[1])
    },

    getFeatureGroups() {
      const result: FeatureGroup[] = []
      for (const { title, features } of this.groups) {
        if (features.length === 0) {
          continue
        }
        result.push({
          title,
          features: features.map((name) => this.flags[name as FlagName]),
        })
      }
      return result
    },
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
        if (flag && flag.status === SWITCHABLE) {
          this.setPreferredState(name as FlagName, state)
        }
      })
    },
    /**
     * Write the current state of the feature flags to the cookie. These cookies
     * are read in the corresponding `initFromCookies` method.
     */
    writeToCookie() {
      const featuresCookie = useCookie<OpenverseCookieState["features"]>(
        "features",
        persistentCookieOptions
      )
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
      const sessionFeaturesCookie = useCookie<
        OpenverseCookieState["sessionFeatures"]
      >("sessionFeatures", sessionCookieOptions)
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
        value: LocationQueryValue | LocationQueryValue[]
      ): value is FeatureState =>
        typeof value === "string" && ["on", "off"].includes(value)
      const isValidEntry = (
        entry: [string, LocationQueryValue | LocationQueryValue[]]
      ): entry is [`ff_${FlagName}`, FeatureState] =>
        isValidName(entry[0]) && isValidValue(entry[1])

      Object.entries(query)
        .filter(isValidEntry)
        .forEach(([name, state]) => {
          // TODO: type `FlagName` should be inferred by TS
          const flagName = name.substring(3) as FlagName
          const flag = this.flags[flagName]
          if (flag.status === SWITCHABLE && flag.supportsQuery !== false) {
            this.setPreferredState(flagName, state)
          }
        })
    },
    setPreferredState(name: FlagName, toState: FeatureState) {
      const flag = this.flags[name]
      if (flag.status === SWITCHABLE) {
        flag.preferredState = toState
        flag.state = toState
      }
    },
    updateStorage(name: FlagName) {
      const flag = this.flags[name]
      if (flag.storage === COOKIE) {
        this.writeToCookie()
      } else if (flag.storage === SESSION) {
        this.writeToSession()
      }
      if (name === "analytics") {
        this.syncAnalyticsWithLocalStorage()
      }
    },
    /**
     * Toggle the feature flag of the given name to the given preferred state.
     *
     * @param name - the name of the flag to toggle
     * @param targetState - the desired state of the feature flag
     */
    toggleFeature(name: string, targetState: FeatureState) {
      if (!isFlagName(name)) {
        throw new Error(`Toggling invalid feature flag: ${name}`)
      }
      const flag = this.flags[name]
      if (flag.status === SWITCHABLE) {
        this.setPreferredState(name, targetState)
        this.updateStorage(name)
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
      storage.value = this.flags.analytics.state === ON ? null : true
    },

    isSwitchable(name: string) {
      if (!isFlagName(name)) {
        throw new Error(`Invalid feature flag accessed: ${name}`)
      }
      return this.flags[name].status === SWITCHABLE
    },
    /**
     * Proxy for `featureState` to simplify the majority of flag state checks.
     *
     * Prefer this for most use cases over using `featureState` directly.
     *
     * @returns `true` if the flag is on, false otherwise
     */
    isOn(name: string) {
      if (!isFlagName(name)) {
        throw new Error(`Invalid feature flag accessed: ${name}`)
      }
      return this.flags[name].state === ON
    },
  },
})
