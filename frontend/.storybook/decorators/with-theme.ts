import { watch, onMounted, reactive, h } from "vue"
import { useEffect, useGlobals } from "@storybook/preview-api"

import { EffectiveColorMode } from "~/types/ui"

import { useDarkMode } from "~/composables/use-dark-mode"
import { useUiStore } from "~/stores/ui"

import VThemeSelect from "~/components/VThemeSelect/VThemeSelect.vue"

type ThemeCssClass = `${EffectiveColorMode}-mode`
const cssClassToTheme = (
  cssClass: ThemeCssClass | undefined
): EffectiveColorMode | undefined => cssClass?.split("-")[0]
const isEffectiveColorMode = (
  value: string | undefined
): value is EffectiveColorMode => ["light", "dark"].includes(value)

const setElementTheme = (el: HTMLElement, cssClass: ThemeCssClass) => {
  if (cssClass === "dark-mode") {
    el.classList.add("dark-mode")
    el.classList.remove("light-mode")
    document.documentElement.style.setProperty(
      "--color-bg-curr-page",
      "#0d0d0d"
    )
  } else {
    el.classList.add("light-mode")
    el.classList.remove("dark-mode")

    document.documentElement.style.setProperty(
      "--color-bg-curr-page",
      "#ffffff"
    )
  }
}

const themeState = reactive<{ value: EffectiveColorMode }>({ value: "light" })

/**
 * Decorator to add the Storybook theme switcher to the addon toolbar, and the Openverse
 * theme switcher to the bottom of the screen.
 * We cannot use the toolbar during the tests that open an iframe without the toolbars,
 * so we need to add the theme switcher to the bottom of the screen.
 * The state of both is kept in sync.
 */
export const WithTheme = (story) => {
  const [globals, updateGlobals] = useGlobals()
  themeState.value = globals.theme

  useEffect(() => {
    themeState.value = globals.theme
  }, [globals.theme])

  return {
    components: { story },
    setup() {
      const { cssClass } = useDarkMode()
      const uiStore = useUiStore()

      watch(
        themeState,
        (newTheme) => {
          if (isEffectiveColorMode(newTheme.value)) {
            uiStore.setColorMode(newTheme.value)
          }
        },
        { immediate: true }
      )

      watch(
        cssClass,
        (newCssClass) => {
          setElementTheme(document.body, newCssClass)
          const theme = cssClassToTheme(newCssClass)
          if (theme) {
            updateGlobals({ theme })
          }
        },
        { immediate: true }
      )

      onMounted(() => {
        document.body.classList.add("bg-default")
      })

      // Set the height to the full height of the Storybook iframe minus the padding
      // to position the theme switcher at the bottom of the screen.
      return () =>
        h("div", { class: "relative", style: "height: calc(100dvh - 32px);" }, [
          h(story()),
          h(
            "div",
            { class: "absolute bottom-0", id: "storybook-theme-switcher" },
            [h(VThemeSelect)]
          ),
        ])
    },
  }
}
