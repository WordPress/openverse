<template>
  <section
    :aria-label="$t('media-details.reuse.title').toString()"
    class="media-reuse"
  >
    <h3 class="text-2xl md:text-3xl mb-6">
      {{ $t('media-details.reuse.title') }}
    </h3>
    <div v-if="media.license_url" class="grid md:grid-cols-2 gap-6">
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
