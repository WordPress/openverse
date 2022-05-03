import { defineStore } from 'pinia'

import featureData from '~~/feat/feature-flags.json'

import { warn } from '~/utils/console'

import type { FeatureFlag } from '~/types/feature-flag'
import type { FeatureState, FlagStatus } from '~/constants/feature-flag'
import {
  ENABLED,
  SWITCHABLE,
  ON,
  OFF,
  DISABLED,
} from '~/constants/feature-flag'
import { LOCAL, DEPLOY_ENVS, DeployEnv } from '~/constants/deploy-env'

export interface FeatureFlagState {
  flags: Record<keyof typeof featureData['features'], FeatureFlag>
}

const FEATURE_FLAG = 'feature_flag'

/**
 * Get the status of the flag. If the flag status is environment dependent, this
 * function will use the flag status for the current environment based on the
 * `DEPLOYMENT_ENV` environment variable.
 *
 * @param flag - the flag for which to get the status
 */
export const getFlagStatus = (flag: FeatureFlag): FlagStatus => {
  const deployEnv = (process.env.DEPLOYMENT_ENV ?? LOCAL) as DeployEnv
  if (typeof flag.status === 'string') return flag.status
  else {
    const envIndex = DEPLOY_ENVS.indexOf(deployEnv)
    for (let i = envIndex; i < DEPLOY_ENVS.length; i += 1) {
      if (DEPLOY_ENVS[i] in flag.status) return flag.status[DEPLOY_ENVS[i]]
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
  if (status === SWITCHABLE)
    return flag.preferredState ?? flag.defaultState ?? OFF
  if (status === ENABLED) return ON
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
     */
    featureState:
      (state: FeatureFlagState) =>
      (name: keyof typeof featureData['features']): FeatureState => {
        if (name in state.flags) return getFeatureState(state.flags[name])
        else {
          warn(`Invalid feature flag accessed: ${name}`)
          return ON
        }
      },
    /**
     * Get the mapping of switchable features to their preferred states.
     */
    flagStateMap: (state: FeatureFlagState): Record<string, FeatureState> => {
      const featureMap: Record<string, FeatureState> = {}
      Object.entries(state.flags).forEach(([name, flag]) => {
        if (getFlagStatus(flag) === SWITCHABLE)
          featureMap[name] = getFeatureState(flag)
      })
      return featureMap
    },
  },
  actions: {
    /**
     * Given a list of key value pairs of flags and their preferred states,
     * populate the store state to match the cookie.
     *
     * @param cookies - mapping of feature flags and their preferred states
     */
    initFromCookies(cookies: Record<string, FeatureState>) {
      Object.entries(this.flags).forEach(([name, flag]) => {
        if (getFlagStatus(flag) === SWITCHABLE)
          flag.preferredState = cookies[name]
      })
    },
    /**
     * Toggle the feature flag of the given name to the given preferred state.
     *
     * @param name - the name of the flag to toggle
     * @param targetState - the desired state of the feature flag
     */
    toggleFeature(
      name: keyof typeof featureData['features'],
      targetState: FeatureState
    ) {
      const flag = this.flags[name]
      if (getFlagStatus(flag) === SWITCHABLE) flag.preferredState = targetState
      else warn(`Cannot set preferred state for non-switchable flag: ${name}`)
    },
  },
})
