import { useDarkMode } from "#imports"

import { ref, watch, onMounted, h } from "vue"

import VThemeSelect from "~/components/VThemeSelect/VThemeSelect.vue"

export const WithThemeSwitcher = (story) => {
  return {
    components: { story },
    setup() {
      const element = ref()
      const { cssClass } = useDarkMode()

      onMounted(() => {
        watch(cssClass, async (newClass, oldClass) => {
          if (element.value) {
            element.value.ownerDocument
              .querySelector("#storybook-root")
              .classList.add("bg-default")
            element.value.ownerDocument.body.classList.add(newClass)
            if (oldClass) {
              element.value.ownerDocument.body.classList.remove(oldClass)
            }
          }
        })
      })
      return () =>
        h("div", { ref: element }, [
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
