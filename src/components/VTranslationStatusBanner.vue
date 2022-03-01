<template>
  <VNotificationBanner v-show="!shouldHideBanner" @close="dismissBanner">
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
        {{ bannerLocale.name }}
      </template>
    </i18n>
  </VNotificationBanner>
</template>
<script>
import useI18nSync from '~/composables/use-i18n-sync'

import VLink from '~/components/VLink.vue'
import VNotificationBanner from '~/components/VNotificationBanner.vue'

export default {
  name: 'VTranslationStatusBanner',
  components: {
    VLink,
    VNotificationBanner,
  },
  setup() {
    const { shouldHideBanner, bannerLocale, translationLink, dismissBanner } =
      useI18nSync()

    return {
      dismissBanner,
      shouldHideBanner,
      bannerLocale,
      translationLink,
    }
  },
}
</script>
