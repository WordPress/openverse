import Vue from "vue"

import { ref, watch, onMounted } from "@nuxtjs/composition-api"
import { useEffect } from "@storybook/client-api"
import { useNuxtApp } from "#app"

const languageDirection = Vue.observable({ value: "ltr" })

export const WithRTL = (story, context) => {
  useEffect(() => {
    languageDirection.value = context.globals.languageDirection
  }, [context.globals.languageDirection])

  return {
    template: `<div ref="element"><story /></div>`,
    components: { story },
    setup() {
      const element = ref()
      const { $i18n: i18n } = useNuxtApp()
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
