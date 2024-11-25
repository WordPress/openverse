<script setup lang="ts">
import VLink from "~/components/VLink.vue"
import VSvg from "~/components/VSvg/VSvg.vue"

withDefaults(
  defineProps<{
    mode?: "dark" | "light"
  }>(),
  { mode: "light" }
)
</script>

<template>
  <VLink
    href="https://wordpress.org"
    :aria-label="$t('footer.wordpressAffiliation', { wordpress: 'WordPress' })"
    class="hover:no-underline"
    :class="
      mode === 'dark'
        ? 'text-white focus-visible:outline-yellow-3'
        : 'text-default'
    "
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
