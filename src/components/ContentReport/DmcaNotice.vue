<template>
  <div>
    <i18n
      path="photo-details.content-report.dmca.content"
      tag="p"
      class="block px-6 mt-10 text-center"
    >
      <template #link>
        <a
          :aria-label="$t('photo-details.aria.dmca')"
          :href="dmcaFormUrl"
          target="_blank"
          rel="noopener"
          >{{ $t('photo-details.content-report.dmca.link') }}</a
        >
      </template>
    </i18n>

    <i18n
      path="photo-details.content-report.dmca.provider"
      tag="p"
      class="block px-6 mt-4 text-center"
    >
      <template #link>
        <a
          :aria-label="
            $t('photo-details.aria.provider-report-form', {
              provider: providerName,
            })
          "
          :href="imageURL"
          target="_blank"
          rel="noopener"
          >{{ providerName }}</a
        >
      </template>
    </i18n>

    <button
      class="button is-text tiny mt-4"
      @click="onBackClick()"
      @keyup.enter="onBackClick()"
    >
      <span
        ><i class="icon chevron-left mr-2" />
        {{ $t('photo-details.content-report.back') }}</span
      >
    </button>
  </div>
</template>

<script>
export default {
  name: 'DmcaNotice',
  props: ['dmcaFormUrl', 'imageURL', 'providerName'],
  methods: {
    onBackClick() {
      this.$emit('onBackClick')
    },
  },
}
</script>
