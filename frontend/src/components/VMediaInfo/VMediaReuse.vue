<script setup lang="ts">
import type { Media } from "~/types/media"

import VCopyLicense from "~/components/VMediaInfo/VCopyLicense.vue"
import VMediaLicense from "~/components/VMediaInfo/VMediaLicense.vue"

defineProps<{ media: Media }>()
</script>

<template>
  <section :aria-label="$t('mediaDetails.reuse.title')" class="media-reuse">
    <h2 class="heading-6 md:heading-5 mb-4">
      {{ $t("mediaDetails.reuse.title") }}
    </h2>
    <p class="description-regular">
      {{
        $t("mediaDetails.reuse.description", {
          media: media.frontendMediaType,
        })
      }}
    </p>
    <p
      v-if="media.frontendMediaType === 'image'"
      class="description-regular mt-3"
    >
      {{ $t("mediaDetails.reuse.copyrightDisclaimer") }}
    </p>
    <div v-if="media.license_url" class="mt-8 grid gap-6 md:grid-cols-2">
      <VMediaLicense
        :license="media.license"
        :license-url="media.license_url"
        :license-version="media.license_version"
      />
      <VCopyLicense :media="media" />
    </div>
  </section>
</template>
