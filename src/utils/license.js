// There are six CC licenses and two Public Domain tools (PDM and CC0,
// which are not licenses in the legal sense.
// FAQ on CC and PDM: https://wiki.creativecommons.org/wiki/CC0_FAQ#What_is_CC0.3F
// Information on CC licenses: https://creativecommons.org/about/cclicenses/
// In code, for conciseness, we call all of them 'License'
/** @typedef {'cc0'|'pdm'|'by'|'by-sa'|'by-nc'|'by-nd'|'by-nc-nd'|'by-nc-sa'} License */

/** @typedef {'CC0'|'PDM'|'CC BY'|'CC BY-SA'|'CC BY-NC'|'CC BY-ND'|'CC BY-NC-ND'|'CC BY-NC-SA'} LicenseName */

// There are several versions of the licenses, and PDM has no version
// https://wiki.creativecommons.org/wiki/License_Versions
/** @typedef {'1.0'|'2.0'|'2.5'|'3.0'|'4.0'|''} LicenseVersion */

/**
 * Capitalized full license name from license slug and version:
 * ('by-sa', '4.0') -> 'CC BY-SA 4.0'
 * @param {License} license
 * @param {LicenseVersion} license_version
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
 * @param {License|LicenseName|''} licenseOrMark
 * @return {asserts licenseOrMark is Exclude<'pdm' | 'cc0', License | LicenseName | ''>} false if licenseOrMark is CC0 or PDM, true otherwise
 */
export const isLicense = (licenseOrMark = '') => {
  return !['pdm', 'cc0'].includes(licenseOrMark.toLowerCase())
}

/**
 * Returns true if argument is PDM or CC0
 * @param {License|LicenseName|''} licenseOrMark
 * @return {boolean}
 */
export const isPublicDomain = (licenseOrMark = '') => {
  return ['pdm', 'cc0'].includes(licenseOrMark.toLowerCase())
}
