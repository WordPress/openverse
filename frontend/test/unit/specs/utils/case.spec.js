import { camelCase, capitalCase } from "~/utils/case"

describe("camelCase", () => {
  it.each`
    input            | output
    ${"media"}       | ${"media"}
    ${"mediaTitle"}  | ${"mediaTitle"}
    ${"Media Title"} | ${"mediaTitle"}
    ${"media title"} | ${"mediaTitle"}
    ${"media-title"} | ${"mediaTitle"}
    ${"media_title"} | ${"mediaTitle"}
  `("returns $output for $input", ({ input, output }) => {
    expect(camelCase(input)).toBe(output)
  })
})

describe("capitalCase", () => {
  it.each`
    input            | output
    ${"media"}       | ${"Media"}
    ${"mediaTitle"}  | ${"Media Title"}
    ${"Media Title"} | ${"Media Title"}
    ${"media title"} | ${"Media Title"}
    ${"media-title"} | ${"Media Title"}
    ${"media_title"} | ${"Media Title"}
  `("returns $output for $input", ({ input, output }) => {
    expect(capitalCase(input)).toBe(output)
  })
})
