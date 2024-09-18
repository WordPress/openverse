import { watch, onMounted, reactive, h } from "vue"
import { useEffect } from "@storybook/preview-api"

import { EffectiveColorMode } from "~/types/ui"

import { useDarkMode } from "~/composables/use-dark-mode"
import { useUiStore } from "~/stores/ui"

import VThemeSelect from "~/components/VThemeSelect/VThemeSelect.vue"

const themeState = reactive<{ value: EffectiveColorMode }>({ value: "light" })

const setElementTheme = (
  el: HTMLElement,
  cssClass: `${EffectiveColorMode}-mode`
) => {
  if (cssClass === "dark-mode") {
    el.classList.add("dark-mode")
    el.classList.remove("light-mode")
  } else {
    el.classList.add("light-mode")
    el.classList.remove("dark-mode")
  }
}

/**
 * Decorator to add the Storybook theme switcher to the addon toolbar, and the Openverse
 * theme switcher to the bottom of the screen.
 * We cannot use the toolbar during the tests that open an iframe without the toolbars,
 * so we need to add the theme switcher to the bottom of the screen.
 * The state of both is kept in sync.
 */
export const WithTheme = (story, context) => {
  useEffect(() => {
    themeState.value = context.globals.theme
  }, [context.globals.theme])

  return {
    components: { story },
    setup() {
      const { cssClass } = useDarkMode()
      const uiStore = useUiStore()

      onMounted(() => {
        document.body.classList.add("bg-default")

        watch(
          themeState,
          (newTheme) => {
            if (["light", "dark"].includes(newTheme.value)) {
              uiStore.setColorMode(newTheme.value)
            }
          },
          { immediate: true }
        )

        watch(
          cssClass,
          (newCssClass) => {
            setElementTheme(document.body, newCssClass)
          },
          { immediate: true }
        )
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
