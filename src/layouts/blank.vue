<template>
  <div>
    <VMigrationNotice v-show="isReferredFromCc" />
    <VTranslationStatusBanner />
    <Nuxt />
  </div>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { useNavStore } from '~/stores/nav'

import VTranslationStatusBanner from '~/components/VTranslationStatusBanner.vue'
import VMigrationNotice from '~/components/VMigrationNotice.vue'

export default defineComponent({
  name: 'BlankLayout',
  components: { VMigrationNotice, VTranslationStatusBanner },
  setup() {
    const navStore = useNavStore()
    const isReferredFromCc = computed(() => navStore.isReferredFromCc)
    return { isReferredFromCc }
  },
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
})
</script>
