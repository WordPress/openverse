import Vue from 'vue'

import { ref, watch, useContext, onMounted } from '@nuxtjs/composition-api'
import { useEffect } from '@storybook/client-api'

const languageDirection = Vue.observable({ value: 'ltr' })

export const WithRTL = (story, context) => {
  useEffect(() => {
    languageDirection.value = context.globals.languageDirection
  }, [context.globals.languageDirection])

  return {
    template: `<div ref="element"><story /></div>`,
    components: { story },
    setup() {
      const element = ref()
      const { i18n } = useContext()
      onMounted(() => {
        watch(
          languageDirection,
          (direction) => {
            i18n.localeProperties.dir = direction.value
            if (element.value) {
              element.value.ownerDocument.documentElement.setAttribute(
                'dir',
                direction?.value ?? 'ltr'
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
