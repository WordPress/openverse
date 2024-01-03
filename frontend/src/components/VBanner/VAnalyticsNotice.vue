<template>
  <VNotificationBanner
    v-bind="$attrs"
    id="analytics"
    nature="info"
    :close-button-label="$t('notification.analytics.close')"
    @close="$emit('close')"
  >
    <i18n-t tag="span" keypath="notification.analytics.text">
      <template #link>
        <VLink :href="privacyPath" class="text-curr underline">{{
          $t("notification.analytics.link")
        }}</VLink>
      </template>
    </i18n-t>
  </VNotificationBanner>
</template>

<script lang="ts">
import { useLocalePath } from "#imports"

import { computed, defineComponent } from "vue"

import { defineEvent } from "~/types/emits"

import VLink from "~/components/VLink.vue"
import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

export default defineComponent({
  name: "VAnalyticsNotice",
  components: { VLink, VNotificationBanner },
  inheritAttrs: false,
  emits: {
    close: defineEvent(),
  },
  setup() {
    const localePath = useLocalePath()
    const privacyPath = computed(() => localePath("/privacy"))

    return {
      privacyPath,
    }
  },
})
</script>
