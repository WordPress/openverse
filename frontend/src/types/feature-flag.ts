import type {
  FeatureState,
  FlagStatus,
  Storage,
} from "~/constants/feature-flag"
import type { DeployEnv } from "~/constants/deploy-env"

export interface FeatureFlag {
  status: FlagStatus | Record<DeployEnv, FlagStatus>
  description?: string
  data?: unknown

  defaultState?: FeatureState
  preferredState?: FeatureState // only set for switchable flag with known preference

  supportsQuery?: boolean // default: true

  storage: Storage
}
