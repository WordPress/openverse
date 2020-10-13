<template>
  <div class="padding-horizontal-bigger padding-vertical-small donation-banner">
    <p class="has-text-centered-mobile">
      {{ donationText }}
    </p>

    <div class="donation-banner__actions">
      <a
        href="https://www.classy.org/give/297881/#!/donation/checkout"
        target="_blank"
        class="button is-success small"
        @click="handleDonateClick"
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
import GoogleAnalytics from '@/analytics/GoogleAnalytics'
import { DonateLinkClick, DonateBannerClose } from '@/analytics/events'
import { ExperimentData } from '@/abTests/experiments/donationLanguage'
import { JOINED_AB_TEST_EXPERIMENT } from '@/store-modules/mutation-types'
import { CONVERT_AB_TEST_EXPERIMENT } from '@/store-modules/action-types'

export default {
  name: 'DonationBanner',
  data: function () {
    return {
      caseA: true,
    }
  },
  computed: {
    donationText() {
      return this.caseA
        ? this.$t('header.donation-banner.description')
        : this.$t('header.donation-banner.alternative-description')
    },
  },
  created() {
    this.unsubscribe = this.$store.subscribe((mutation, state) => {
      if (mutation.type === JOINED_AB_TEST_EXPERIMENT) {
        const experiment = state.experiments.find(
          (exp) => exp.name === ExperimentData.EXPERIMENT_NAME
        )
        this.caseA = experiment.case === ExperimentData.DONATION_GENERAL_CASE
      }
    })
  },
  beforeDestroy() {
    this.unsubscribe()
  },
  methods: {
    onDismiss() {
      this.$emit('onDismiss')
      GoogleAnalytics().sendEvent(DonateBannerClose())
    },
    handleDonateClick() {
      this.$store.dispatch(CONVERT_AB_TEST_EXPERIMENT, {
        experimentName: ExperimentData.EXPERIMENT_NAME,
      })
      GoogleAnalytics().sendEvent(DonateLinkClick('banner'))
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

// double selector to increase specificity (to override other issues)
.dismiss-button.dismiss-button {
  color: $color-dark-success;
  padding: $space-small calc(#{$space-normal} + 0.2rem) !important;
  white-space: nowrap;
}
</style>
