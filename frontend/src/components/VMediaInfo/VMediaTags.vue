<template>
  <div class="flex flex-col gap-6 sm:gap-8">
    <div v-if="tagsByType.source.length > 0">
      <h3 class="label-regular mb-2">
        {{ $t("mediaDetails.tags.source.heading") }}
      </h3>
      <VCollapsibleTagSection
        :media-type="mediaType"
        :tags="tagsByType.source"
      />
    </div>
    <div v-if="tagsByType.generated.length > 0">
      <div class="flex gap-2">
        <h3
          id="generated-tags"
          class="label-regular align-start mb-2 flex flex-row"
        >
          {{ $t("mediaDetails.tags.generated.heading") }}
        </h3>
        <VLink class="label-regular" :href="generatedTagsPath">{{
          $t("mediaDetails.tags.generated.pageTitle")
        }}</VLink>
      </div>
      <VCollapsibleTagSection
        :media-type="mediaType"
        :tags="tagsByType.generated"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import type { SupportedMediaType } from "~/constants/media"
import type { Tag } from "~/types/media"

import VCollapsibleTagSection from "~/components/VMediaInfo/VCollapsibleTagSection.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VMediaTags",
  components: { VCollapsibleTagSection, VLink },
  props: {
    tags: {
      type: Array as PropType<Tag[]>,
      required: true,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
    provider: {
      type: String as PropType<string>,
      required: true,
    },
  },
  setup(props) {
    const tagsByType = computed(() => {
      const generatedTags = []
      const sourceTags = []
      for (const tag of props.tags) {
        if (
          tag.unstable__provider &&
          tag.unstable__provider !== props.provider
        ) {
          generatedTags.push(tag)
        } else {
          sourceTags.push(tag)
        }
      }
      return { generated: generatedTags, source: sourceTags }
    })

    const { app } = useContext()

    const generatedTagsPath = computed(() => app.localePath("/generated-tags"))

    return { generatedTagsPath, tagsByType }
  },
})
</script>
