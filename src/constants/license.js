export const CC_LICENSES = [
  'by',
  'by-sa',
  'by-nd',
  'by-nc',
  'by-nc-sa',
  'by-nc-nd',
]

export const NON_CC_LICENSES = ['cc0', 'pdm']

export const DEPRECATED_LICENSES = ['nc-sampling+', 'sampling+']

export const ALL_LICENSES = [
  ...CC_LICENSES,
  ...NON_CC_LICENSES,
  ...DEPRECATED_LICENSES,
]

export const LICENSE_ICON_MAPPING = {
  by: 'by',
  nc: 'nc',
  nd: 'nd',
  sa: 'sa',
  cc0: 'cc0',
  pdm: 'pdm',
}
