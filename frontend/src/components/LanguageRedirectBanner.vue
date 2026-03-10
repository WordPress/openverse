<script setup lang="ts">
import { useCookie } from '#app'

const unsupportedLocale = useCookie<string>('unsupported_language_code')

function closeBanner() {
  unsupportedLocale.value = null
}
</script>

<template>
  <div
    v-if="unsupportedLocale"
    class="language-redirect-banner"
    role="alert"
  >
    <span>
      We don’t have translations for
      <strong>{{ unsupportedLocale }}</strong>.
      Showing the English version instead.
    </span>

    <button
      type="button"
      aria-label="Dismiss language notice"
      @click="closeBanner"
    >
      ×
    </button>
  </div>
</template>

<style scoped>
.language-redirect-banner {
  background: #fff4cc;
  color: #333;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}
</style>
