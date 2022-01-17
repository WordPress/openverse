<template>
  <div class="photo columns is-desktop px-6 md:px-14 pb-16">
    <div class="column is-three-fifths photo_image-ctr mt-4">
      <a
        v-if="shouldShowBreadcrumb"
        class="flex photo_breadcrumb text-left mb-4 lg:ms-0 text-dark-gray font-semibold caption"
        :href="breadCrumbURL"
        @click.prevent="goBackToSearchResults"
      >
        <VIcon :icon-path="icons.chevronLeft" class="me-2" />
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

      <p class="caption text-left text-dark-gray mt-4 mb-2 ms-4 lg:ms-0">
        {{ $t('photo-details.legal-disclaimer') }}
      </p>

      <VButton
        variant="action-button"
        size="disabled"
        class="report py-2 mt-2"
        @click="reportForm.toggleVisibility"
      >
        {{ $t('photo-details.content-report.title') }}
        <VIcon :icon-path="icons.flag" class="text-trans-blue ms-2 text-sm" />
      </VButton>
      <VContentReportForm
        v-if="isReportFormVisible"
        :image="image"
        :provider-name="providerName"
        data-testid="content-report-form"
        class="mt-2 text-left"
        @close-form="reportForm.close()"
      />
    </div>
    <div
      role="region"
      :aria-label="$t('photo-details.aria.details')"
      class="column image-info md:ms-10"
    >
      <div class="my-4">
        <h1 v-if="isLoaded" class="text-6xl">{{ image.title }}</h1>
        <i18n
          v-if="image.creator"
          class="caption"
          path="photo-details.creator"
          tag="span"
        >
          <template #name>
            <a
              v-if="image.creator_url"
              :aria-label="
                $t('photo-details.aria.creator-url', { creator: image.creator })
              "
              :href="image.creator_url"
              @click="linkClicked.creatorLink"
            >
              {{ image.creator }}
            </a>
            <span v-else>{{ image.creator }}</span>
          </template>
        </i18n>
      </div>
      <section class="tabs">
        <div role="tablist" :aria-label="$t('photo-details.aria.details')">
          <button
            id="reuse"
            role="tab"
            type="button"
            aria-controls="tab-reuse"
            :aria-selected="activeTab === 0"
            :class="tabClass(0, 'tab')"
            @click.prevent="setActiveTab(0)"
          >
            {{ $t('photo-details.reuse.title') }}
          </button>
          <button
            id="information"
            role="tab"
            type="button"
            aria-controls="tab-information"
            :aria-selected="activeTab === 1"
            :class="tabClass(1, 'tab')"
            @click.prevent="setActiveTab(1)"
          >
            {{ $t('photo-details.information.title') }}
          </button>
        </div>
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
            :license-url="license.url"
            :full-license-name="license.fullName"
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
            :license-url="license.url"
            :full-license-name="license.fullName"
            :image-width="imageWidth"
            :image-height="imageHeight"
            :image-type="imageType"
          />
        </div>
      </section>

      <a
        data-testid="source-button"
        :href="image.foreign_landing_url"
        target="_blank"
        rel="noopener"
        class="button is-success mb-2 mt-4"
        @click="linkClicked.photoSource"
      >
        {{ $t('photo-details.weblink') }}
        <VIcon
          class="inline ms-4 pt-1 text-base text-light-gray"
          :icon-path="icons.externalLink"
          rtl-flip
        />
      </a>

      <ReuseSurvey :image="image" />
    </div>
  </div>
</template>

<script>
import { computed, ref, useContext, useRouter } from '@nuxtjs/composition-api'

import { USAGE_DATA } from '~/constants/store-modules'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/constants/usage-data-analytics-types'

import { getFullLicenseName } from '~/utils/license'

import chevronLeft from '~/assets/icons/chevron-left.svg'
import flag from '~/assets/icons/flag.svg'
import externalLink from '~/assets/icons/external-link.svg'

import ReuseSurvey from '~/components/ImageDetails/ReuseSurvey.vue'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VContentReportForm from '~/components/VContentReport/VContentReportForm.vue'
import SketchFabViewer from '~/components/SketchFabViewer.vue'
import ImageInfo from '~/components/ImageDetails/ImageInfo.vue'
import ImageAttribution from '~/components/ImageDetails/ImageAttribution.vue'

export default {
  name: 'VPhotoDetails',
  components: {
    ImageAttribution,
    ImageInfo,
    ReuseSurvey,
    SketchFabViewer,
    VButton,
    VIcon,
    VContentReportForm,
  },
  props: [
    'image',
    'breadCrumbURL',
    'shouldShowBreadcrumb',
    'imageWidth',
    'imageHeight',
    'imageType',
    'thumbnail',
  ],
  setup(props, { emit }) {
    const { store } = useContext()
    const router = useRouter()
    const sketchFabfailure = ref(false)
    const activeTab = ref(0)
    const isReportFormVisible = ref(false)

    const imgUrl = computed(() => {
      return isLoaded.value ? props.image.url : props.thumbnail
    })
    const isLoaded = computed(() => props.image && !!props.image.url)
    const providerName = computed(() => {
      return props.image
        ? store.getters['provider/getProviderName'](props.image.provider)
        : ''
    })
    /** @type {ComputedRef<null|string>} */
    const sketchFabUid = computed(() => {
      if (props.image.source !== 'sketchfab' || this.sketchFabfailure) {
        return null
      }

      return props.image.url
        .split('https://media.sketchfab.com/models/')[1]
        .split('/')[0]
    })

    const fullLicenseName = computed(() => {
      return props.image
        ? getFullLicenseName(props.image.license, props.image.license_version)
        : ''
    })
    const licenseUrl = computed(
      () => `${props.image.license_url}?ref=openverse`
    )

    const goBackToSearchResults = () => {
      router.back()
    }
    const onImageLoad = (event) => emit('onImageLoaded', event)

    const tabClass = (tabIdx, tabClass) => {
      return {
        [tabClass]: true,
        'is-active': tabIdx === activeTab.value,
      }
    }
    const setActiveTab = (tabIdx) => (activeTab.value = tabIdx)

    const onCloseReportForm = () => (isReportFormVisible.value = false)
    const toggleReportFormVisibility = () => {
      isReportFormVisible.value = !isReportFormVisible.value
    }

    const sendEvent = (eventType) => {
      const eventData = {
        eventType,
        resultUuid: props.image.id,
      }
      store.dispatch(`${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`, eventData)
    }
    const onPhotoSourceLinkClicked = () =>
      sendEvent(DETAIL_PAGE_EVENTS.SOURCE_CLICKED)
    const onPhotoCreatorLinkClicked = () =>
      sendEvent(DETAIL_PAGE_EVENTS.CREATOR_CLICKED)

    return {
      imgUrl,
      onImageLoad,
      isLoaded,
      sketchFabUid,
      sketchFabfailure,
      isReportFormVisible,
      goBackToSearchResults,
      linkClicked: {
        photoSource: onPhotoSourceLinkClicked,
        creatorLink: onPhotoCreatorLinkClicked,
      },
      license: {
        url: licenseUrl.value,
        fullName: fullLicenseName.value,
      },
      reportForm: {
        close: onCloseReportForm,
        toggleVisibility: toggleReportFormVisibility,
      },
      icons: {
        chevronLeft,
        externalLink,
        flag,
      },

      activeTab,
      tabClass,
      setActiveTab,

      providerName,
    }
  },
}
</script>

<style lang="scss" scoped>
.photo_image.loading {
  width: 100%;
}

.photo_image-ctr {
  overflow: hidden;
  text-align: center;

  img {
    position: relative;
    width: 100%;
    height: auto;
    max-height: 44rem;
    max-width: 100%;
    object-fit: contain;
  }
}

.tab:first-child {
  margin-inline-start: 0;
}
</style>
