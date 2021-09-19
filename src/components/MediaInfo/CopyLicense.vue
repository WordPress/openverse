<template>
  <div class="copy-license">
    <h5 class="b-header mb-6">
      {{ $t('media-details.reuse.copy-license.title') }}
    </h5>
    <section class="tabs boxed">
      <div
        role="tablist"
        :aria-label="$t('media-details.reuse.copy-license.title')"
      >
        <button
          v-for="tab in tabs"
          :id="tab.id"
          :key="tab.id"
          role="tab"
          :aria-selected="activeTab === tab.id"
          :aria-controls="`tab-${tab.name}`"
          :class="tabClass(tab.id, 'tab')"
          @click.prevent="setActiveTab(tab.id)"
          @keyup.enter.prevent="setActiveTab(tab.id)"
        >
          {{ $t(`media-details.reuse.copy-license.${tab.name}`) }}
        </button>
      </div>
      <div
        id="tab-rich"
        aria-labelledby="rich"
        role="tabpanel"
        :class="tabClass(0, 'tabs-panel')"
        tabindex="0"
      >
        <i18n
          id="attribution"
          path="media-details.reuse.credit.text"
          tag="span"
          class="photo_usage-attribution block"
        >
          <template #title>
            <a
              :href="media.foreign_landing_url"
              target="_blank"
              rel="noopener"
              @click="onPhotoSourceLinkClicked"
              @keyup.enter="onPhotoSourceLinkClicked"
              >{{ mediaTitle }}</a
            ></template
          >
          <template #creator>
            <i18n
              v-if="media.creator"
              path="media-details.reuse.credit.creator-text"
              tag="span"
            >
              <template #creator-name>
                <a
                  v-if="media.creator_url"
                  :href="media.creator_url"
                  target="_blank"
                  rel="noopener"
                  @click="onPhotoCreatorLinkClicked"
                  @keyup.enter="onPhotoCreatorLinkClicked"
                  >{{ media.creator }}</a
                >
                <span v-else>{{ media.creator }}</span>
              </template>
            </i18n>
          </template>
          <template #marked-licensed>
            {{
              isPublicDomain
                ? $t('media-details.reuse.credit.marked')
                : $t('media-details.reuse.credit.licensed')
            }}
          </template>
          <template #license>
            <a
              class="photo_license"
              :href="ccLicenseURL"
              target="_blank"
              rel="noopener"
            >
              {{ fullLicenseName.toUpperCase() }}
            </a>
          </template>
        </i18n>

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
            class="textarea font-mono p-0"
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
        <i18n
          id="attribution-text"
          path="media-details.reuse.credit.text"
          tag="p"
        >
          <template #title>
            {{ mediaTitle }}
          </template>
          <template #creator>
            <i18n
              v-if="media.creator"
              path="media-details.reuse.credit.creator-text"
            >
              <template #creator-name>
                {{ media.creator }}
              </template>
            </i18n>
          </template>
          <template #marked-licensed>
            {{
              isPublicDomain
                ? $t('media-details.reuse.credit.marked')
                : $t('media-details.reuse.credit.licensed')
            }}
          </template>
          <template #license> {{ fullLicenseName.toUpperCase() }}</template>
          <template #view-legal>
            <i18n path="media-details.reuse.credit.view-legal-text">
              <template #terms-copy>
                {{
                  isPublicDomain
                    ? $t('media-details.reuse.credit.terms-text')
                    : $t('media-details.reuse.credit.copy-text')
                }}
              </template>
              <template v-if="ccLicenseURL" #URL>
                {{ ccLicenseURL }}
              </template>
            </i18n>
          </template>
        </i18n>
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
import { COPY_ATTRIBUTION } from '~/constants/action-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import { isPublicDomain } from '~/utils/license'
import { ATTRIBUTION } from '~/constants/store-modules'

export default {
  name: 'CopyLicense',
  props: {
    media: {},
    fullLicenseName: String,
    attributionHtml: String,
    ccLicenseURL: String,
  },
  data() {
    return {
      activeTab: 0,
      tabs: [
        { id: 0, name: 'rich' },
        { id: 1, name: 'html' },
        { id: 2, name: 'plain' },
      ],
    }
  },
  computed: {
    isPublicDomain() {
      return isPublicDomain(this.$props.fullLicenseName)
    },
    mediaTitle() {
      const title = this.$props.media.title
      return !['Audio', 'Image'].includes(title)
        ? `"${title}"`
        : this.$t('media-details.reuse.image')
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
        resultUuid: this.$props.media.id,
      })
    },
    onCopyAttribution(type, event) {
      this.$store.dispatch(`${ATTRIBUTION}/${COPY_ATTRIBUTION}`, {
        type,
        content: event.content,
      })
      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.ATTRIBUTION_CLICKED)
    },
    onPhotoSourceLinkClicked() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: this.$props.media.id,
      })
    },
    onPhotoCreatorLinkClicked() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.CREATOR_CLICKED,
        resultUuid: this.$props.media.id,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
textarea {
  border: none;
  resize: none;
}

.copy-attribution {
  margin-left: auto;
}
</style>
