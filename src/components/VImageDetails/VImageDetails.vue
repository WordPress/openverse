<template>
  <section class="w-full">
    <div class="flex flex-row justify-between items-center mb-6">
      <h3 class="text-2xl md:text-3xl">
        {{ $t('image-details.information.title') }}
      </h3>
      <VContentReportPopover :media="image" />
    </div>
    <ul v-if="image && image.tags" class="flex flex-wrap gap-2 mb-6">
      <VMediaTag
        v-for="(tag, index) in image.tags.filter((i) => !!i)"
        :key="index"
        tag="li"
        >{{ tag.name }}</VMediaTag
      >
    </ul>
    <dl>
      <div>
        <dt>{{ $t('image-details.information.type') }}</dt>
        <dd class="uppercase">{{ imgType }}</dd>
      </div>
      <div v-if="providerName !== sourceName">
        <dt>{{ $t('image-details.information.provider') }}</dt>
        <dd>{{ providerName }}</dd>
      </div>
      <div>
        <dt>{{ $t('image-details.information.source') }}</dt>
        <dd>
          <VLink :href="image.foreign_landing_url" class="text-pink">{{
            sourceName
          }}</VLink>
        </dd>
      </div>
      <div>
        <dt>{{ $t('image-details.information.dimensions') }}</dt>
        <dd>
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          {{ imageWidth }} &times; {{ imageHeight }}
          {{ $t('image-details.information.pixels') }}
        </dd>
      </div>
    </dl>
  </section>
</template>

<script>
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'

import VContentReportPopover from '~/components/VContentReport/VContentReportPopover.vue'
import VMediaTag from '~/components/VMediaTag/VMediaTag.vue'

const VImageDetails = defineComponent({
  name: 'VImageDetails',
  components: { VContentReportPopover, VMediaTag },
  props: {
    image: {
      type: Object,
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
    const { store, i18n } = useContext()

    const imgType = computed(() => {
      if (props.imageType) {
        if (props.imageType.split('/').length > 1) {
          return props.imageType.split('/')[1].toUpperCase()
        }
        return props.imageType
      }
      return i18n.t('image-details.information.unknown')
    })

    function getProviderName(nameCode) {
      return nameCode ? store.getters['provider/getProviderName'](nameCode) : ''
    }

    const providerName = computed(() => getProviderName(props.image.provider))

    const sourceName = computed(() => getProviderName(props.image.source))

    return { imgType, providerName, sourceName }
  },
})
export default VImageDetails
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
  @apply font-bold mt-2;
}
</style>
