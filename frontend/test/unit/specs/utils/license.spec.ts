import { i18n } from "~~/test/unit/test-utils/i18n"

import { getFullLicenseName, getElements } from "~/utils/license"
import type { License, LicenseVersion } from "~/constants/license"

describe("getFullLicenseName", () => {
  it.each`
    license           | licenseVersion | sendI18n | fullName
    ${"by"}           | ${""}          | ${false} | ${"CC BY"}
    ${"by-nc-nd"}     | ${"4.0"}       | ${false} | ${"CC BY-NC-ND 4.0"}
    ${"cc0"}          | ${""}          | ${false} | ${"CC0"}
    ${"sampling+"}    | ${""}          | ${false} | ${"CC Sampling+"}
    ${"nc-sampling+"} | ${""}          | ${false} | ${"CC NC-Sampling+"}
    ${"pdm"}          | ${""}          | ${false} | ${"PDM"}
    ${"pdm"}          | ${""}          | ${true}  | ${"Public Domain Mark"}
  `(
    "returns license name for license $license and version $licenseVersion",
    ({
      license,
      licenseVersion,
      sendI18n,
      fullName,
    }: {
      license: License
      licenseVersion: LicenseVersion
      sendI18n: boolean
      fullName: string
    }) => {
      expect(
        getFullLicenseName(license, licenseVersion, sendI18n ? i18n : null)
      ).toBe(fullName)
    }
  )
})

describe("getElements", () => {
  it.each`
    license           | icons
    ${"by"}           | ${["cc", "by"]}
    ${"by-sa"}        | ${["cc", "by", "sa"]}
    ${"by-nd"}        | ${["cc", "by", "nd"]}
    ${"by-nc"}        | ${["cc", "by", "nc"]}
    ${"by-nc-sa"}     | ${["cc", "by", "nc", "sa"]}
    ${"by-nc-nd"}     | ${["cc", "by", "nc", "nd"]}
    ${"nc-sampling+"} | ${["cc", "nc", "sampling-plus"]}
    ${"sampling+"}    | ${["cc", "sampling-plus"]}
    ${"pdm"}          | ${["pd"]}
    ${"cc0"}          | ${["cc", "zero"]}
  `(
    "returns $icons for $license",
    ({ license, icons }: { license: License; icons: string[] }) => {
      expect(getElements(license)).toEqual(icons)
    }
  )
})
