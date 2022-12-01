<template>
  <VNotificationBanner
    :id="bannerKey"
    variant="informational"
    data-testid="banner-translation"
    @close="$emit('close')"
  >
    {{
      // eslint-disable-next-line @intlify/vue-i18n/no-raw-text
      '⚠️'
    }}
    <i18n path="notification.translation.text">
      <template #link>
        <VLink :href="currentLocale.link" class="underline">{{
          $t('notification.translation.link')
        }}</VLink>
      </template>
      <template #locale>
        {{ currentLocale.name }}
      </template>
    </i18n>
  </VNotificationBanner>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { BannerId } from '~/types/banners'

import { useUiStore } from '~/stores/ui'

import { createTranslationLink } from '~/utils/translation-banner'

import VLink from '~/components/VLink.vue'
import VNotificationBanner from '~/components/VBanner/VNotificationBanner.vue'

export default defineComponent({
  name: 'VTranslationStatusBanner',
  components: {
    VLink,
    VNotificationBanner,
  },
  props: {
    bannerKey: {
      type: String as PropType<BannerId>,
      required: true,
    },
  },
  setup() {
    const uiStore = useUiStore()

    /**
     * Returns the link to the GlotPress project for the current locale and the locale native name.
     */
    const currentLocale = computed(() => {
      const localeObject = uiStore.currentLocale

      return {
        link: createTranslationLink(localeObject),
        name: localeObject.name,
      }
    })

    return {
      currentLocale,
    }
  },
})
</script>
