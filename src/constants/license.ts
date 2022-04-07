import by from '~/assets/licenses/by.svg'
import nc from '~/assets/licenses/nc.svg'
import nd from '~/assets/licenses/nd.svg'
import sa from '~/assets/licenses/sa.svg'
import cc0 from '~/assets/licenses/cc0.svg'
import pdm from '~/assets/licenses/pdm.svg'
import sampling from '~/assets/licenses/sampling.svg'
import samplingPlus from '~/assets/licenses/sampling-plus.svg'
import ccLogo from '~/assets/licenses/cc-logo.svg'

export const CC_LICENSES = [
  'by',
  'by-sa',
  'by-nd',
  'by-nc',
  'by-nc-sa',
  'by-nc-nd',
] as const

export const DEPRECATED_CC_LICENSES = ['nc-sampling+', 'sampling+'] as const

export const PUBLIC_DOMAIN_MARKS = ['pdm', 'cc0'] as const

export const ACTIVE_LICENSES = [...PUBLIC_DOMAIN_MARKS, ...CC_LICENSES] as const

export const ALL_LICENSES = [
  ...ACTIVE_LICENSES,
  ...DEPRECATED_CC_LICENSES,
] as const

export type License = typeof ALL_LICENSES[number]

export const LICENSE_VERSIONS = ['', '1.0', '2.0', '2.5', '3.0', '4.0'] as const

export type LicenseVersion = typeof LICENSE_VERSIONS[number]

export const licenseIcons = {
  ccLogo,
  by,
  nc,
  nd,
  sa,
  cc0,
  pdm,
  sampling,
  'sampling+': samplingPlus,
}
export type LicenseElement = keyof typeof licenseIcons
