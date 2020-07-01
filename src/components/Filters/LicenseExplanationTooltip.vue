<template>
  <div class="license-explanation-tooltip padding-small">
    <h5 class="b-header">
      {{ $t('browse-page.license-description.title') }} {{ license.toUpperCase() }}
    </h5>
    <license-explanations :license="license" />
    <p class="caption is-pulled-right margin-small">
      Read more about the license
      <a target="_blank" :href="`${getLicenseDeedLink(license)}`">here</a>
    </p>
  </div>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations'

export default {
  name: 'license-explanation-tooltip',
  props: ['license'],
  components: {
    LicenseExplanations,
  },
  methods: {
    getLicenseDeedLink(licenseTerm) {
      return `https://creativecommons.org/licenses/${licenseTerm}/4.0/?ref=ccsearch&atype=rich`
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all.sass';

// from http://www.cssarrowplease.com/
.license-explanation-tooltip {
  position: absolute;
  background: #ffffff;
  border: 2px solid #d8d8d8;
  z-index: 10;
  width: 20rem;
  box-shadow: 10px 10px 10px -10px rgba(0, 0, 0, 0.25);
  @include desktop {
    margin-left: 20.5rem;
    margin-top: -2.6rem;
  }
  @include touch {
    margin-top: 0.5rem;
  }
}
.license-explanation-tooltip:after,
.license-explanation-tooltip:before {
  @include desktop {
    right: 100%;
    top: 7%;
  }
  @include touch {
    bottom: 100%;
    left: 10%;
  }
  border: solid transparent;
  content: ' ';
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}

.license-explanation-tooltip:after {
  border-color: rgba(255, 255, 255, 0);
  border-width: 10px;

  @include desktop {
    border-right-color: #ffffff;
    margin-top: 3px;
  }
  @include touch {
    border-bottom-color: #ffffff;
    margin-left: 258px;
  }
}
.license-explanation-tooltip:before {
  border-color: rgba(120, 120, 120, 0);
  border-width: 13px;

  @include desktop {
    border-right-color: #d8d8d8;
    margin-top: 0px;
  }
  @include touch {
    border-bottom-color: #d8d8d8;
    margin-left: 255px;
  }
}
</style>
