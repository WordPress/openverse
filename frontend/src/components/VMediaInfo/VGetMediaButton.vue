<template>
  <VButton
    as="VLink"
    :href="media.foreign_landing_url"
    size="large"
    variant="filled-pink"
    has-icon-end
    show-external-icon
    :external-icon-size="6"
    class="description-bold"
    :send-external-link-click-event="false"
    @click="sendGetMediaEvent"
  >
    {{ $t(`${mediaType}Details.weblink`) }}
  </VButton>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import type { SupportedMediaType } from "~/constants/media"
import type { Media } from "~/types/media"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VGetMediaButton",
  components: { VButton },
  props: {
    media: {
      type: Object as PropType<Media>,
      required: true,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()

    const sendGetMediaEvent = () => {
      sendCustomEvent("GET_MEDIA", {
        id: props.media.id,
        provider: props.media.provider,
        mediaType: props.mediaType,
      })
    }
    return {
      sendGetMediaEvent,
    }
  },
})
</script>
