import { useI18n } from "#imports"

import { ref, watch, onMounted, reactive } from "vue"

import { useEffect } from "@storybook/client-api"

const languageDirection = reactive({ value: "ltr" })

export const WithRTL = (story, context) => {
  useEffect(() => {
    languageDirection.value = context.globals.languageDirection
  }, [context.globals.languageDirection])

  return {
    template: `<div ref="element"><story /></div>`,
    components: { story },
    setup() {
      const element = ref()
      const { i18n } = useI18n({ useScope: "global" })
      onMounted(() => {
        watch(
          languageDirection,
          (direction) => {
            i18n.localeProperties.dir = direction.value
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
      return { element }
    },
  }
}
