import { describe, expect, it } from "vitest"
import { replacePlaceholders } from "~~/i18n/scripts/translations.mjs"

const replace = (json) =>
  replacePlaceholders(
    json,
    "ko.json",
    { count: 0, keys: {} },
    { count: 0, keys: {} }
  )

describe("replacePlaceholders", () => {
  it("replaces placeholders with vue-i18n interpolations", () => {
    expect(
      replace({ a: "###openverse### and ###link###", b: "###sources-link###" })
    ).toEqual({ a: "{'Openverse'} and {link}", b: "{sourcesLink}" })
  })

  it.each([
    ["###'Openverse'### 프로젝트는 ###link###를 준수합니다."],
    ["{'Openverse'} 프로젝트는 {link}를 준수합니다."],
  ])(
    "keeps translations that contain the quoted Openverse name: %s",
    (value) => {
      expect(replace({ key: value })).toEqual({
        key: "Openverse 프로젝트는 {link}를 준수합니다.",
      })
    }
  )

  it("empties translations with broken placeholders", () => {
    expect(replace({ key: "#link and #### text" })).toEqual({ key: "" })
  })
})
