<template>
  <div class="copy-license margin-vertical-normal">
    <!-- TODO: change to accommodate different sentence structures -->
    <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
    <h5 class="b-header margin-bottom-small">
      {{ $t('photo-details.reuse.copy-license.title') }}
    </h5>
    <section class="search-tabs boxed">
      <div
        role="tablist"
        :aria-label="$t('photo-details.reuse.copy-license.title')"
      >
        <button
          id="rich"
          role="tab"
          :aria-selected="activeTab == 0"
          aria-controls="tab-rich"
          :class="tabClass(0, 'tab')"
          @click.prevent="setActiveTab(0)"
          @keyup.enter.prevent="setActiveTab(0)"
        >
          {{ $t('photo-details.reuse.copy-license.rich') }}
        </button>
        <button
          id="html"
          role="tab"
          :aria-selected="activeTab == 1"
          aria-controls="tab-html"
          :class="tabClass(1, 'tab')"
          @click.prevent="setActiveTab(1)"
          @keyup.enter.prevent="setActiveTab(1)"
        >
          {{ $t('photo-details.reuse.copy-license.html') }}
        </button>
        <button
          id="text"
          role="tab"
          :aria-selected="activeTab == 2"
          aria-controls="tab-text"
          :class="tabClass(2, 'tab')"
          @click.prevent="setActiveTab(2)"
          @keyup.enter.prevent="setActiveTab(2)"
        >
          {{ $t('photo-details.reuse.copy-license.plain') }}
        </button>
      </div>
      <div
        id="tab-rich"
        aria-labelledby="rich"
        role="tabpanel"
        :class="tabClass(0, 'tabs-panel')"
        tabindex="0"
      >
        <span
          id="attribution"
          ref="photoAttribution"
          class="photo_usage-attribution is-block"
        >
          <a
            :href="image.foreign_landing_url"
            target="_blank"
            rel="noopener"
            @click="onPhotoSourceLinkClicked"
            @keyup.enter="onPhotoSourceLinkClicked"
            >{{ imageTitle }}</a
          >
          <span v-if="image.creator">
            by
            <a
              v-if="image.creator_url"
              :href="image.creator_url"
              target="_blank"
              rel="noopener"
              @click="onPhotoCreatorLinkClicked"
              @keyup.enter="onPhotoCreatorLinkClicked"
              >{{ image.creator }}</a
            >
            <span v-else>{{ image.creator }}</span>
          </span>
          {{ isTool ? 'is marked with' : 'is licensed under' }}
          <a
            class="photo_license"
            :href="licenseURL"
            target="_blank"
            rel="noopener"
          >
            {{ fullLicenseName.toUpperCase() }}
          </a>
        </span>

        <CopyButton
          id="copyattr-rich"
          el="#attribution"
          @copied="(e) => onCopyAttribution('Rich Text', e)"
        />
      </div>
      <div
        id="tab-html"
        aria-labelledby="html"
        role="tabpanel"
        :class="tabClass(1, 'tabs-panel')"
        tabindex="0"
      >
        <label for="attribution-html">
          <textarea
            id="attribution-html"
            class="textarea monospace is-paddingless"
            :value="attributionHtml"
            cols="30"
            rows="4"
            readonly="readonly"
          />
        </label>
        <CopyButton
          id="copyattr-html"
          el="#attribution-html"
          @copied="(e) => onCopyAttribution('HTML Embed', e)"
        />
      </div>
      <div
        id="tab-text"
        aria-labelledby="text"
        role="tabpanel"
        :class="tabClass(2, 'tabs-panel')"
        tabindex="0"
      >
        <p
          id="attribution-text"
          ref="photoAttribution"
          class="photo_usage-attribution is-block"
        >
          {{ imageTitle }}
          <span v-if="image.creator"> by {{ image.creator }} </span>
          {{ isTool ? 'is marked under' : 'is licensed with' }}
          {{ fullLicenseName.toUpperCase() }}. To
          {{ isTool ? 'view the terms' : 'view a copy of this license' }}, visit
          <template v-if="licenseURL">
            {{ licenseURL.substring(0, licenseURL.indexOf('?')) }}
          </template>
        </p>

        <CopyButton
          id="copyattr-plain"
          el="#attribution-text"
          @copied="(e) => onCopyAttribution('Plain Text', e)"
        />
      </div>
    </section>
  </div>
</template>

<script>
import CopyButton from '~/components/CopyButton'
import { COPY_ATTRIBUTION } from '~/store-modules/action-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'

export default {
  name: 'CopyLicense',
  components: {
    CopyButton,
  },
  props: ['image', 'fullLicenseName', 'attributionHtml', 'licenseURL'],
  data() {
    return {
      activeTab: 0,
    }
  },
  computed: {
    isTool() {
      return (
        this.fullLicenseName.includes('cc0') ||
        this.fullLicenseName.includes('pdm')
      )
    },
    imageTitle() {
      const title = this.$props.image.title
      return title !== 'Image' ? `"${title}"` : 'Image'
    },
  },
  methods: {
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      }
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx
    },
    sendDetailPageEvent(eventType) {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType,
        resultUuid: this.$props.image.id,
      })
    },
    onCopyAttribution(type, event) {
      this.$store.dispatch(COPY_ATTRIBUTION, { type, content: event.content })
      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.ATTRIBUTION_CLICKED)
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
@import '~/styles/tabs.scss';

textarea {
  border: none;
  resize: none;
}

.copy-attribution {
  margin-left: auto;
}
</style>
