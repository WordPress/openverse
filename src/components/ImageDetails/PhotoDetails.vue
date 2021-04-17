<template>
  <div class="photo columns is-desktop is-marginless padding-bottom-xl">
    <div class="column is-three-fifths photo_image-ctr margin-top-normal">
      <a
        v-if="shouldShowBreadcrumb"
        class="is-block photo_breadcrumb has-text-left margin-left-normal margin-bottom-normal has-text-grey-dark has-text-weight-semibold caption"
        :href="breadCrumbURL"
        @click.prevent="onGoBackToSearchResults"
        @keyup.enter.prevent="onGoBackToSearchResults"
      >
        <i class="icon chevron-left margin-right-small" />
        {{ $t('photo-details.back') }}
      </a>

      <img
        v-show="!sketchFabUid"
        :class="{ photo_image: true, loading: !isLoaded }"
        :src="imgUrl"
        :alt="image.title"
        @load="onImageLoad"
      />

      <SketchFabViewer
        v-if="sketchFabUid"
        :uid="sketchFabUid"
        @failure="sketchFabfailure = true"
      />

      <LegalDisclaimer />

      <div class="margin-bottom-smaller has-text-left">
        <button
          class="button is-text tiny is-paddingless report is-shadowless"
          @click.prevent="toggleReportFormVisibility"
          @keypress.enter.prevent="toggleReportFormVisibility"
        >
          <span class="has-color-tomato margin-left-small">
            <i class="icon flag margin-right-small" />
            {{ $t('photo-details.content-report.title') }}
          </span>
        </button>
      </div>
      <div class="margin-top-small has-text-left">
        <ContentReportForm
          v-if="isReportFormVisible"
          :image="image"
          data-testid="content-report-form"
        />
      </div>
    </div>
    <div
      role="region"
      :aria-label="$t('photo-details.aria.details')"
      class="column image-info margin-left-xl"
    >
      <div class="margin-top-normal margin-bottom-small">
        <h1 class="title is-5 b-header">
          {{ image.title }}
        </h1>
        <span v-if="image.creator" class="caption has-text-weight-semibold">
          <!-- TODO: need to change to accommodate sentence order in different languages -->
          <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
          by
          <!-- eslint-enable -->
          <a
            v-if="image.creator_url"
            :aria-label="'author' + image.creator"
            :href="image.creator_url"
            @click="onPhotoCreatorLinkClicked"
            @keyup.enter="onPhotoCreatorLinkClicked"
          >
            {{ image.creator }}
          </a>
          <span v-else>{{ image.creator }}</span>
        </span>
      </div>
      <section class="tabs">
        <div role="tablist" :aria-label="$t('photo-details.aria.details')">
          <button
            id="reuse"
            role="tab"
            aria-controls="tab-reuse"
            :aria-selected="activeTab === 0"
            :class="tabClass(0, 'tab')"
            @click.prevent="setActiveTab(0)"
            @keyup.enter.prevent="setActiveTab(0)"
          >
            {{ $t('photo-details.reuse.title') }}
          </button>
          <button
            id="information"
            role="tab"
            aria-controls="tab-information"
            :aria-selected="activeTab === 1"
            :class="tabClass(1, 'tab')"
            @click.prevent="setActiveTab(1)"
            @keyup.enter.prevent="setActiveTab(1)"
          >
            {{ $t('photo-details.information.title') }}
          </button>
          <button
            v-if="socialSharingEnabled"
            id="social-sharing"
            role="tab"
            aria-controls="tab-social-sharing"
            :aria-selected="activeTab == 2"
            :class="tabClass(2, 'a')"
            @click.prevent="setActiveTab(2)"
            @keyup.enter.prevent="setActiveTab(2)"
          >
            {{ $t('photo-details.share') }}
          </button>
        </div>
        <!-- <section class="photo_info-ctr tabs-content">-->
        <div
          id="tab-reuse"
          role="tabpanel"
          aria-labelledby="reuse"
          tabindex="0"
          :class="tabClass(0, 'tabs-panel')"
        >
          <ImageAttribution
            data-testid="image-attribution"
            :image="image"
            :cc-license-u-r-l="ccLicenseURL"
            :full-license-name="fullLicenseName"
            :attribution-html="attributionHtml()"
          />
        </div>
        <div
          id="tab-information"
          role="tabpanel"
          aria-labelledby="information"
          tabindex="0"
          :class="tabClass(1, 'tabs-panel')"
        >
          <ImageInfo
            data-testid="image-info"
            :image="image"
            :cc-license-u-r-l="ccLicenseURL"
            :full-license-name="fullLicenseName"
            :image-width="imageWidth"
            :image-height="imageHeight"
            :image-type="imageType"
          />
        </div>
        <div
          id="tab-social-sharing"
          role="tabpanel"
          aria-labelledby="social-sharing"
          tabindex="0"
          :class="tabClass(2, 'tabs-panel')"
        >
          <ImageSocialShare
            v-if="socialSharingEnabled"
            :image="image"
            data-testid="social-share"
          />
        </div>
      </section>

      <a
        v-if="activeTab < 2"
        data-testid="source-button"
        :href="image.foreign_landing_url"
        target="_blank"
        rel="noopener"
        class="button is-success margin-bottom-small"
        @click="onPhotoSourceLinkClicked"
        @keyup.enter="onPhotoSourceLinkClicked"
      >
        {{ $t('photo-details.weblink') }}
        <i
          class="icon external-link margin-left-normal is-size-6 padding-top-smaller has-text-grey-lighter"
        />
      </a>

      <ReuseSurvey v-if="activeTab < 2" :image="image" />
    </div>
  </div>
</template>

<script>
import { TOGGLE_REPORT_FORM_VISIBILITY } from '~/store-modules/mutation-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import attributionHtml from '~/utils/attributionHtml'

export default {
  name: 'PhotoDetails',
  props: [
    'image',
    'breadCrumbURL',
    'shouldShowBreadcrumb',
    'query',
    'imageWidth',
    'imageHeight',
    'imageType',
    'socialSharingEnabled',
    'thumbnail',
  ],
  data() {
    return {
      sketchFabfailure: false,
      activeTab: 0,
    }
  },
  computed: {
    imgUrl() {
      return this.image && this.image.url ? this.image.url : this.thumbnail
    },
    isLoaded() {
      return this.image && !!this.image.url
    },
    sketchFabUid() {
      if (this.image.source !== 'sketchfab' || this.sketchFabfailure) {
        return null
      }

      return this.image.url
        .split('https://media.sketchfab.com/models/')[1]
        .split('/')[0]
    },
    isReportFormVisible() {
      return this.$store.state.isReportFormVisible
    },
    fullLicenseName() {
      const license = this.image.license
      const version = this.image.license_version

      if (license) {
        return license.toLowerCase() === 'cc0'
          ? `${license} ${version}`
          : `CC ${license} ${version}`
      }
      return ''
    },
    ccLicenseURL() {
      return `${this.image.license_url}?ref=ccsearch`
    },
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.back()
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event)
    },
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      }
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx
    },
    attributionHtml() {
      const licenseURL = `${this.ccLicenseURL}&atype=html`
      return attributionHtml(this.image, licenseURL, this.fullLicenseName)
    },
    toggleReportFormVisibility() {
      this.$store.commit(TOGGLE_REPORT_FORM_VISIBILITY)
    },
    onPhotoSourceLinkClicked() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: this.$props.image.id,
      })
    },
    onPhotoCreatorLinkClicked() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.CREATOR_CLICKED,
        resultUuid: this.$props.image.id,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '~/styles/photodetails.scss';
@import '~/styles/tabs.scss';

@include touch {
  .image-info {
    margin-left: 0 !important;
  }
}
</style>
