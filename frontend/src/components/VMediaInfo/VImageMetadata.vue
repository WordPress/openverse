<template>
  <dl>
    <div>
      <dt>{{ $t("mediaDetails.information.type") }}</dt>
      <dd class="uppercase">{{ imgType }}</dd>
    </div>
    <div v-if="image.providerName !== image.sourceName">
      <dt>{{ $t("mediaDetails.providerLabel") }}</dt>
      <dd>{{ image.providerName }}</dd>
    </div>
    <div>
      <dt>{{ $t("mediaDetails.sourceLabel") }}</dt>
      <dd>
        <VLink :href="image.foreign_landing_url" class="text-pink">{{
          image.sourceName
        }}</VLink>
      </dd>
    </div>
    <div>
      <dt>{{ $t("imageDetails.information.dimensions") }}</dt>
      <dd>
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        {{ width }} &times; {{ height }}
        {{ $t("imageDetails.information.pixels") }}
      </dd>
    </div>
  </dl>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { ImageDetail } from "~/types/media"
import { useI18n } from "~/composables/use-i18n"

import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VImageMetadata",
  components: { VLink },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
      required: true,
    },
    width: {
      type: Number,
    },
    height: {
      type: Number,
    },
    imageType: {
      type: String,
    },
  },
  setup(props) {
    const i18n = useI18n()

    const imgType = computed(() => {
      if (props.imageType) {
        if (props.imageType.split("/").length > 1) {
          return props.imageType.split("/")[1].toUpperCase()
        }
        return props.imageType
      }
      return i18n.t("mediaDetails.information.unknown")
    })

    return {
      imgType,
    }
  },
})
</script>

<style scoped>
dl {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  grid-gap: 1rem;
}

dt,
dd {
  @apply text-sm md:text-base;
}

dd {
  @apply mt-2 font-semibold;
}
</style>
