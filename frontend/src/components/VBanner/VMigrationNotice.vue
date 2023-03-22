<template>
  <VNotificationBanner
    id="cc-referral"
    variant="announcement"
    @close="$emit('close')"
  >
    {{
      $t("migration-notice.intro", {
        "cc-search": "CC Search",
        openverse: "Openverse",
        wordpress: "WordPress",
      })
    }}
    <i18n tag="span" path="migration-notice.more">
      <template #read-more>
        <VLink
          class="font-bold text-white underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
        >
          {{ $t("migration-notice.read") }}
        </VLink>
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
})
</script>
