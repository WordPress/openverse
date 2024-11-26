import { useI18n } from "#imports"
import { ref, watch, onMounted, reactive, h } from "vue"

import { useEffect } from "@storybook/preview-api"

const languageDirection = reactive({ value: "ltr" })

export const WithRTL = (story, context) => {
  useEffect(() => {
    languageDirection.value = context.globals.languageDirection
  }, [context.globals.languageDirection])

  return {
    components: { story },
    setup() {
      const element = ref()
      const i18n = useI18n({ useScope: "global" })

      onMounted(() => {
        watch(
          languageDirection,
          async (direction) => {
            await i18n.setLocale(direction.value === "rtl" ? "ar" : "en")

            if (element.value) {
              element.value.ownerDocument.documentElement.setAttribute(
                "dir",
                direction?.value ?? "ltr"
              )
            }
          },
          { immediate: true }
        )
      })
      return () => h("div", { ref: element }, [h(story())])
    },
  }
}
