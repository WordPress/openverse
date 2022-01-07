<template>
  <div class="my-10">
    <span class="block px-6 text-center">
      {{ $t('photo-details.content-report.thanks') }}
    </span>
    <i18n
      path="photo-details.content-report.provider"
      tag="span"
      class="block px-6 mt-10 text-center"
    >
      <template #link>
        <a
          :aria-label="
            $t('photo-details.aria.provider-report-form', { provider })
          "
          :href="imageUrl"
          target="_blank"
          rel="noopener"
          >{{ provider }}</a
        >
      </template>
    </i18n>
  </div>
</template>

<script>
export default {
  name: 'DoneMessage',
  props: ['imageUrl', 'provider'],
}
</script>
