<template>
  <section
    :aria-label="$t('media-details.reuse.title').toString()"
    class="media-reuse"
  >
    <h2 class="mb-4 heading-6 md:heading-5">
      {{ $t('media-details.reuse.title') }}
    </h2>
    <p class="text-base font-normal leading-[130%]">
      {{
        $t('media-details.reuse.description', {
          media: media.frontendMediaType,
        })
      }}
    </p>
    <div v-if="media.license_url" class="mt-8 grid gap-6 md:grid-cols-2">
      <VMediaLicense
        :license="media.license"
        :license-url="media.license_url"
        :full-license-name="fullLicenseName"
      />
      <VCopyLicense :media="media" />
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { getFullLicenseName } from '~/utils/license'

import type { Media } from '~/models/media'

import { useI18n } from '~/composables/use-i18n'

import VCopyLicense from '~/components/VMediaInfo/VCopyLicense.vue'
import VMediaLicense from '~/components/VMediaInfo/VMediaLicense.vue'

export default defineComponent({
  name: 'VMediaReuse',
  components: { VCopyLicense, VMediaLicense },
  props: {
    media: {
      type: Object as PropType<Media>,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n()

    const fullLicenseName = computed(() =>
      getFullLicenseName(props.media.license, props.media.license_version, i18n)
    )

    return { fullLicenseName }
  },
})
</script>
