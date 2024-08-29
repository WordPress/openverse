import { h, ref } from "vue"

import { useSearchStore } from "~/stores/search"

import VButton from "~/components/VButton.vue"

export const WithTeleportTarget = (story) => {
  return {
    components: { story },
    setup() {
      const isRendered = ref(false)
      const renderStory = () => {
        isRendered.value = true
      }
      // A workaround to make sure that the useStorage is initialized in the child story
      useSearchStore().addRecentSearch("cat")
      return () =>
        h("div", null, [
          isRendered.value
            ? h(story())
            : h(
                VButton,
                { variant: "filled-dark", size: "large", onClick: renderStory },
                { default: () => "Render Story" }
              ),
          h("div"),
          h("div", { id: "teleports" }),
        ])
    },
  }
}
