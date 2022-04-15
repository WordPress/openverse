<template>
  <VNotificationBanner
    :id="bannerKey"
    :enabled="needsTranslationBanner"
    variant="informational"
  >
    {{
      // eslint-disable-next-line @intlify/vue-i18n/no-raw-text
      '⚠️'
    }}
    <i18n path="notification.translation.text">
      <template #link>
        <VLink :href="translationLink" class="underline">{{
          $t('notification.translation.link')
        }}</VLink>
      </template>
      <template #locale>
        {{ name }}
      </template>
    </i18n>
  </VNotificationBanner>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { useI18nSync } from '~/composables/use-i18n-sync'

import VLink from '~/components/VLink.vue'
import VNotificationBanner from '~/components/VNotificationBanner.vue'

export default defineComponent({
  name: 'VTranslationStatusBanner',
  components: {
    VLink,
    VNotificationBanner,
  },
  setup() {
    const { currentLocale, translationLink, needsTranslationBanner } =
      useI18nSync()
    const bannerKey = `translation-${currentLocale.value?.code ?? 'en'}`
    const name = computed(() => currentLocale.value?.name ?? '')
    return {
      needsTranslationBanner,
      bannerKey,
      name,
      translationLink,
    }
  },
})
</script>
