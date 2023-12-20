import Vue from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"

const TestWrapper = Vue.component("TestWrapper", {
  props: ["n", "locale"],
  setup(props) {
    const getLocaleFormattedNumber = useGetLocaleFormattedNumber(props.locale)

    return { getLocaleFormattedNumber }
  },
  template: `<div>{{ getLocaleFormattedNumber(n) }}</div>`,
})

describe("use-get-locale-formatted-number", () => {
  it.each(["ar", "fa", "ckb", "ps"])(
    "should use en formatting for locales like %s that use Eastern Arabic Numerals",
    async (locale) => {
      const { container } = await render(TestWrapper, {
        props: { n: 1000.01, locale },
      })

      expect(container.firstChild.textContent).toEqual(
        (1000.01).toLocaleString("en")
      )
      expect(container.firstChild.textContent).not.toEqual(
        (1000.01).toLocaleString(locale)
      )
    }
  )

  it.each(["pt-br", "en-us", "en-gb", "ru"])(
    "should use the default formatting for locales not matching eastern arabic numeral locales like %s",
    async (locale) => {
      const { container } = await render(TestWrapper, {
        props: { n: 1000.01, locale },
      })

      expect(container.firstChild.textContent).toEqual(
        (1000.01).toLocaleString(locale)
      )
    }
  )
})
