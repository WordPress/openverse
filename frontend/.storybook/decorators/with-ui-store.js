import { ref, onMounted, h } from "vue"

import { useLayout } from "~/composables/use-layout"

export const WithUiStore = (story) => {
  return {
    components: { story },
    setup() {
      const element = ref()
      const { updateBreakpoint } = useLayout()
      onMounted(() => {
        updateBreakpoint()
      })
      return () => h("div", { ref: element }, [h(story())])
    },
  }
}
