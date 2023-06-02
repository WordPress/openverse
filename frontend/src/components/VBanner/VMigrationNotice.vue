<template>
  <VNotificationBanner
    v-bind="$attrs"
    id="cc-referral"
    nature="info"
    :close-button-label="$t('migrationNotice.close')"
    @close="$emit('close')"
  >
    {{
      $t("migrationNotice.intro", {
        ccSearch: "CC Search",
        openverse: "Openverse",
        wordpress: "WordPress",
      })
    }}
    <i18n tag="span" path="migrationNotice.more">
      <template #readMore>
        <VLink
          class="text-curr underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
          >{{ $t("migrationNotice.read") }}</VLink
        >
      </template>
    </i18n>
  </VNotificationBanner>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VMigrationNotice",
  components: { VLink, VNotificationBanner },
  inheritAttrs: false,
})
</script>
