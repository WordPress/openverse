<template>
  <section class="w-full">
    <div class="mb-6 flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t("imageDetails.information.title") }}
      </h2>
      <VContentReportPopover :media="image" />
    </div>
    <ul v-if="image && image.tags" class="mb-6 flex flex-wrap gap-2">
      <VMediaTag v-for="(tag, index) in filteredTags" :key="index" tag="li">{{
        tag.name
      }}</VMediaTag>
    </ul>
    <dl>
      <div>
        <dt>{{ $t("imageDetails.information.type") }}</dt>
        <dd class="uppercase">{{ imgType }}</dd>
      </div>
      <div v-if="image.providerName !== image.sourceName">
        <dt>{{ $t("imageDetails.information.provider") }}</dt>
        <dd>{{ image.providerName }}</dd>
      </div>
      <div>
        <dt>{{ $t("imageDetails.information.source") }}</dt>
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
          {{ imageWidth }} &times; {{ imageHeight }}
          {{ $t("imageDetails.information.pixels") }}
        </dd>
      </div>
    </dl>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useI18n } from "~/composables/use-i18n"

import type { ImageDetail } from "~/types/media"

import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VLink from "~/components/VLink.vue"
import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"

export default defineComponent({
  name: "VImageDetails",
  components: { VContentReportPopover, VLink, VMediaTag },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
      required: true,
    },
    imageWidth: {
      type: Number,
    },
    imageHeight: {
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
      return i18n.t("imageDetails.information.unknown")
    })

    const filteredTags = computed(() => {
      return props.image.tags.filter((i: { name: string }) => !!i)
    })

    return { filteredTags, imgType }
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
