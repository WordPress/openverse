<script setup lang="ts">
import { useLocalePath } from "#imports"
import { computed } from "vue"

import type { SupportedMediaType } from "#shared/constants/media"
import type { Tag } from "#shared/types/media"

import VCollapsibleTagSection from "~/components/VMediaInfo/VCollapsibleTagSection.vue"
import VLink from "~/components/VLink.vue"

const props = defineProps<{
  tags: Tag[]
  mediaType: SupportedMediaType
  provider: string
}>()

const tagsByType = computed(() => {
  const generatedTags = []
  const sourceTags = []
  for (const tag of props.tags) {
    if (tag.unstable__provider && tag.unstable__provider !== props.provider) {
      generatedTags.push(tag)
    } else {
      sourceTags.push(tag)
    }
  }
  return { generated: generatedTags, source: sourceTags }
})

const hasSourceTags = computed(() => tagsByType.value.source.length > 0)
const hasGeneratedTags = computed(() => tagsByType.value.generated.length > 0)

const localePath = useLocalePath()

const tagsPagePath = computed(() => localePath("/tags"))
</script>

<template>
  <div class="flex flex-col gap-6 sm:gap-8">
    <div v-if="hasSourceTags">
      <h3 v-if="hasGeneratedTags" class="label-regular mb-2">
        {{ $t("mediaDetails.tags.source.heading") }}
      </h3>
      <h3 v-else class="sr-only">{{ $t("mediaDetails.tags.title") }}</h3>
      <VCollapsibleTagSection
        :media-type="mediaType"
        :tags="tagsByType.source"
      />
    </div>
    <div v-if="hasGeneratedTags">
      <div class="label-regular mb-2 flex gap-2">
        <h3>{{ $t("mediaDetails.tags.generated.heading") }}</h3>
        <VLink :href="tagsPagePath">{{
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
