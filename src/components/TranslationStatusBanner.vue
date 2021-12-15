<template>
  <NotificationBanner v-show="!shouldHideBanner" @close="dismissBanner">
    {{
      // eslint-disable-next-line @intlify/vue-i18n/no-raw-text
      '⚠️'
    }}
    <i18n path="notification.translation.text">
      <template #link>
        <a :href="translationLink" target="_blank">{{
          $t('notification.translation.link')
        }}</a>
      </template>
      <template #locale>
        {{ bannerLocale.name }}
      </template>
    </i18n>
  </NotificationBanner>
</template>
<script>
import useI18nSync from '~/composables/use-i18n-sync'

export default {
  name: 'TranslationStatusBanner',
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
