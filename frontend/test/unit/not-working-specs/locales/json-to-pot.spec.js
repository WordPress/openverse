import { replaceVarsPlaceholders } from "~/locales/scripts/json-pot-helpers"

describe("replaceVarsPlaceholders", () => {
  it("replaces lower case placeholders", () => {
    const string = "string with a {placeholder}"
    const expected = "string with a ###placeholder###"

    expect(replaceVarsPlaceholders(string)).toEqual(expected)
  })
  /**
   * Replaces placeholders no matter what casing they use
   */
  it("replaces upper case placeholders", () => {
    const string = "{strinG} {WITH} {Placeholders}"
    const expected = "###strinG### ###WITH### ###Placeholders###"

    expect(replaceVarsPlaceholders(string)).toEqual(expected)
  })
  /**
   * Replaces lower- and upper- case placeholders with one or more
   * dashes anywhere in the string
   */
  it("replaces placeholders with dashes", () => {
    const string = "{a-string-and-a-half} {WITH--} {Place-holders}"
    const expected =
      "###a-string-and-a-half### ###WITH--### ###Place-holders###"

    expect(replaceVarsPlaceholders(string)).toEqual(expected)
  })
  /**
   * Does not replace placeholders with anything other than letters and dashes,
   * or ### placeholders
   */
  it("returns the string if no placeholders are found", () => {
    const string =
      "{some{ ###phrase### that {does--not {have.any} {place_holders}"
    const expected =
      "{some{ ###phrase### that {does--not {have.any} {place_holders}"

    expect(replaceVarsPlaceholders(string)).toEqual(expected)
  })
})
