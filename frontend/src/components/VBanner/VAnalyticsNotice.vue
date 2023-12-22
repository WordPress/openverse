<template>
  <VNotificationBanner
    v-bind="$attrs"
    id="analytics"
    nature="info"
    :close-button-label="$t('notification.analytics.close')"
    @close="$emit('close')"
  >
    <i18n tag="span" path="notification.analytics.text">
      <template #link>
        <VLink :href="privacyPath" class="text-curr underline">{{
          $t("notification.analytics.link")
        }}</VLink>
      </template>
    </i18n>
  </VNotificationBanner>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"
import { useContext } from "@nuxtjs/composition-api"

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
    const { app } = useContext()
    const privacyPath = computed(() => app.localePath("/privacy"))

    return {
      privacyPath,
    }
  },
})
</script>
