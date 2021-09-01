/** @typedef {'cc0'|'by'|'by-sa'|'by-nc'|'by-nd'|'by-nc-nd'|'by-nc-sa'|'pdm'} License */

/**
 * Capitalized full license name from license slug and version:
 * ('by-sa', '4.0') -> 'CC BY-SA 4.0'
 * @param {string} license
 * @param {string} license_version
 * @return {string}
 */
export const getFullLicenseName = (license, license_version) => {
  if (!license) {
    return ''
  }
  const licenseUpper = license.toUpperCase()
  return licenseUpper === 'CC0'
    ? `${licenseUpper} ${license_version}`
    : `CC ${licenseUpper} ${license_version}`
}

/**
 * CC licenses have different legal status from the public domain marks
 * such as CC0 and PDM, and need different wording.
 * Returns false if licenseOrMark is CC0 or PDM
 * @param {string} licenseOrMark
 * @return {boolean}
 */
export const checkIsLicense = (licenseOrMark) => {
  const licenseOrMarkLower = licenseOrMark ? licenseOrMark.toLowerCase() : ''
  return (
    !licenseOrMarkLower.includes('pdm') && !licenseOrMarkLower.includes('cc0')
  )
}
