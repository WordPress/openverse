<template>
  <div class="mt-4 mb-2">
    <p class="caption text-left text-dark-gray">
      {{ $t('photo-details.legal-disclaimer') }}
    </p>
  </div>
</template>

<script>
export default {
  name: 'LegalDisclaimer',
}
</script>

<style lang="scss" scoped>
li:before {
  content: '\2022';
  color: #ccc;
  font-weight: bold;
  display: inline-block;
  margin-right: 0.5rem;
  font-size: 1rem;
}
</style>
