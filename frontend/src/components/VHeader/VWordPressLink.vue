<template>
  <VLink
    href="https://wordpress.org"
    :aria-label="t('footer.wordpressAffiliation', { wordpress: 'WordPress' })"
    :class="mode === 'light' ? 'text-dark-charcoal' : 'text-white'"
    class="hover:no-underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
  >
    <i18n-t
      scope="global"
      tag="p"
      keypath="footer.wordpressAffiliation"
      class="label-regular flex flex-row items-center gap-1"
    >
      <template #wordpress>
        <VSvg name="wordpress" class="h-6 w-6" width="24" height="24" />
      </template>
    </i18n-t>
  </VLink>
</template>
<script setup lang="ts">
import { useNuxtApp } from "#imports"

import VLink from "~/components/VLink.vue"
import VSvg from "~/components/VSvg/VSvg.vue"

withDefaults(
  defineProps<{
    mode?: "dark" | "light"
  }>(),
  { mode: "light" }
)
const {
  $i18n: { t },
} = useNuxtApp()
</script>
