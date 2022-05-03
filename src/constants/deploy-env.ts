export const LOCAL = 'local'
export const DEVELOPMENT = 'development'
export const STAGING = 'staging'
export const PRODUCTION = 'production'

// The order of the environments is important. They should be arranged in
// increasing order of code-readiness, from local to production.
export const DEPLOY_ENVS = [LOCAL, DEVELOPMENT, STAGING, PRODUCTION] as const

export type DeployEnv = typeof DEPLOY_ENVS[number]
