<template>
  <div class="padding-horizontal-normal padding-vertical-small donation-banner">
    <p class="has-text-centered-mobile">
      {{ $t('header.donation-banner.description') }}
    </p>

    <div class="donation-banner__actions">
      <a
        href="https://www.classy.org/give/297881/#!/donation/checkout"
        target="_blank"
        class="button is-success small"
      >
        <i
          class="icon cc-letterheart-filled margin-right-small is-size-5 padding-top-smaller"
        />
        {{ $t('header.donation-banner.yes') }}
      </a>
      <button class="button is-text small dismiss-button" @click="onDismiss">
        {{ $t('header.donation-banner.no') }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DonationBanner',
  methods: {
    onDismiss() {
      this.$emit('onDismiss')
    },
  },
}
</script>

<style scoped lang="scss">
@import 'bulma/sass/utilities/_all.sass';
@import '@creativecommons/vocabulary/scss/color.scss';
@import '@creativecommons/vocabulary/scss/spacing.scss';

$bgColor: #e6f6eb;

.donation-banner {
  background-color: $bgColor;

  @include tablet {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.donation-banner__actions {
  display: flex;

  @include mobile {
    margin-top: $space-small;
    justify-content: center;
  }

  @include tablet {
    padding-left: $space-normal;
  }
}

.button {
  text-transform: none;
  font-family: inherit;
}

.dismiss-button {
  color: $color-dark-success;
  padding: $space-small calc(#{$space-normal} + 0.2rem) !important;
  white-space: nowrap;
}
</style>
