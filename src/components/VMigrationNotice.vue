<template>
  <VNotificationBanner
    id="cc-referral"
    :enabled="isReferredFromCc"
    variant="announcement"
  >
    {{
      $t('migration-notice.intro', {
        'cc-search': 'CC Search',
        openverse: 'Openverse',
        wordpress: 'WordPress',
      })
    }}
    <i18n tag="span" path="migration-notice.more">
      <template #read-more>
        <VLink
          class="text-white font-bold underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
          >{{ $t('migration-notice.read') }}</VLink
        >
      </template>
    </i18n>
  </VNotificationBanner>
</template>

<script lang="ts">
import { defineComponent, computed } from '@nuxtjs/composition-api'

import { useNavigationStore } from '~/stores/navigation'

import VNotificationBanner from '~/components/VNotificationBanner.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VMigrationNotice',
  components: { VLink, VNotificationBanner },
  setup() {
    const navigationStore = useNavigationStore()
    const isReferredFromCc = computed(() => navigationStore.isReferredFromCc)
    return { isReferredFromCc }
  },
})
</script>
