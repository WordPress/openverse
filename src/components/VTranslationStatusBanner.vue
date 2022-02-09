<template>
  <VNotificationBanner v-show="!shouldHideBanner" @close="dismissBanner">
    {{
      // eslint-disable-next-line @intlify/vue-i18n/no-raw-text
      '⚠️'
    }}
    <i18n path="notification.translation.text">
      <template #link>
        <a :href="translationLink" target="_blank" class="underline">{{
          $t('notification.translation.link')
        }}</a>
      </template>
      <template #locale>
        {{ bannerLocale.name }}
      </template>
    </i18n>
  </VNotificationBanner>
</template>
<script>
import useI18nSync from '~/composables/use-i18n-sync'
import VNotificationBanner from '~/components/VNotificationBanner.vue'

export default {
  name: 'VTranslationStatusBanner',
  components: {
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
