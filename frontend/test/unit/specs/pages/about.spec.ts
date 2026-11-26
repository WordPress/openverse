import { createI18n } from "vue-i18n"
import { describe, expect, it } from "vitest"
import { screen } from "@testing-library/vue"
import { renderSuspended } from "@nuxt/test-utils/runtime"
import messages from "~~/i18n/locales/en.json"

import AboutPage from "~/pages/about.vue"

const hindi = {
  "externalSourcesPage.new.issue": "मुद्दा",
  "externalSourcesPage.new.email": "ईमेल",
}

const renderInLocale = (locale: "en" | "hi") => {
  const i18n = createI18n({
    locale,
    fallbackLocale: "en",
    legacy: false,
    messages: { en: messages, hi: hindi },
  })
  return renderSuspended(AboutPage, { global: { plugins: [i18n] } })
}

describe("About page", () => {
  it.each`
    locale  | issue       | email
    ${"en"} | ${"issue"}  | ${"email"}
    ${"hi"} | ${"मुद्दा"} | ${"ईमेल"}
  `(
    "external source links are named by their visible text in $locale",
    async ({ locale, issue, email }) => {
      await renderInLocale(locale)

      for (const [text, href] of [
        [issue, "https://github.com/WordPress/openverse/issues"],
        [email, "mailto:openverse@wordpress.org"],
      ]) {
        const link = screen.getByRole("link", { name: text })
        expect(link.getAttribute("href")).toEqual(href)
        expect(link.textContent?.trim()).toEqual(text)
        expect(link.hasAttribute("aria-label")).toBe(false)
      }
    }
  )
})
