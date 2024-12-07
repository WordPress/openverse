<script setup lang="ts">
import VLink from "~/components/VLink.vue"
import VSvg from "~/components/VSvg/VSvg.vue"
</script>

<template>
  <VLink
    href="https://wordpress.org"
    :aria-label="$t('footer.wordpressAffiliation', { wordpress: 'WordPress' })"
    class="text-contrast hover:no-underline focus-visible:outline-focus-ring"
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
