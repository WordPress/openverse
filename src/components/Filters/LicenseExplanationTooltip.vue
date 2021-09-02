<template>
  <div class="license-explanation-tooltip p-2">
    <h5 v-if="!isLicense" class="b-header mb-4">
      {{ isLicense ? $t('browse-page.license-description.title') : '' }}
      {{ license.toUpperCase() }}
    </h5>
    <LicenseElements :license="license" class="tooltip" />
    <i18n
      v-if="!isLicense"
      path="filters.license-explanation.tool"
      tag="p"
      class="caption float-right m-2"
    >
      <template #link>
        <a target="_blank" :href="`${getLicenseDeedLink(license)}`">{{
          $t('filters.license-explanation.link')
        }}</a>
      </template>
    </i18n>
    <i18n
      v-else
      path="filters.license-explanation.license"
      tag="p"
      class="caption float-right m-2"
    >
      <template #link>
        <a target="_blank" :href="`${getLicenseDeedLink(license)}`">{{
          $t('filters.license-explanation.link')
        }}</a>
      </template>
    </i18n>
  </div>
</template>

<script>
import { isLicense } from '~/utils/license'

export default {
  name: 'LicenseExplanationTooltip',

  props: {
    license: {
      type: String,
      required: true,
    },
  },
  computed: {
    isLicense() {
      return isLicense(this.$props.license)
    },
  },
  methods: {
    getLicenseDeedLink(licenseTerm) {
      if (licenseTerm === 'cc0') {
        return 'https://creativecommons.org/publicdomain/zero/1.0/?ref=ccsearch&atype=rich'
      } else if (licenseTerm === 'pdm') {
        return 'https://creativecommons.org/publicdomain/mark/1.0/?ref=ccsearch&atype=rich'
      }
      return `https://creativecommons.org/licenses/${licenseTerm}/4.0/?ref=ccsearch&atype=rich`
    },
  },
}
</script>

<style lang="scss" scoped>
// from http://www.cssarrowplease.com/
.license-explanation-tooltip {
  position: absolute;
  background: #ffffff;
  border: 2px solid #d8d8d8;
  z-index: 400;
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
