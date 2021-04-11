<template>
  <div>
    <i18n
      path="photo-details.content-report.dmca.content"
      tag="p"
      class="is-block padding-horizontal-big margin-top-large has-text-centered"
    >
      <template v-slot:link>
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
      class="is-block padding-horizontal-big margin-top-normal has-text-centered"
    >
      <template v-slot:link>
        <a
          :aria-label="provider + 'form'"
          :href="imageURL"
          target="_blank"
          rel="noopener"
          >{{ providerName }}</a
        >
      </template>
    </i18n>

    <button
      class="button is-text tiny margin-top-normal is-shadowless"
      @click="onBackClick()"
      @keyup.enter="onBackClick()"
    >
      <span
        ><i class="icon chevron-left margin-right-small" />
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
