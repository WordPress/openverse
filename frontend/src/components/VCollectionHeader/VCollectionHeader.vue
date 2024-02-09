<template>
  <div
    class="collection-header grid grid-cols-[1.5rem,1fr] gap-x-2 gap-y-4 md:grid-rows-[auto,auto] md:gap-y-8"
    :class="
      collection === 'tag'
        ? 'tags grid-rows-[auto,auto] md:grid-cols-[2.5rem,1fr]'
        : 'grid-rows-[auto,auto,auto] md:grid-cols-[2.5rem,1fr,auto]'
    "
  >
    <VIcon :name="iconName" :size="isMd ? 10 : 6" class="icon" />
    <h1 class="title text-3xl font-semibold leading-snug md:text-6xl">
      {{ title }}
    </h1>
    <VButton
      v-if="collection !== 'tag' && url"
      as="VLink"
      variant="filled-dark"
      size="medium"
      class="button label-bold !flex-none md:ms-4 md:mt-1"
      has-icon-end
      show-external-icon
      :external-icon-size="6"
      :href="url"
      @click="sendAnalyticsEvent"
      >{{ $t(`collection.link.${collection}`) }}</VButton
    >
    <p
      v-if="collectionParams.collection !== 'creator'"
      class="results caption-regular md:label-regular mt-2 text-dark-charcoal-70 md:mt-0"
    >
      {{ resultsLabel }}
    </p>

    <p
      v-else-if="
        collectionParams.collection === 'creator' && resultsLabel.length === 2
      "
      class="results caption-regular md:label-regular mt-2 text-dark-charcoal-70 md:mt-0"
    >
      {{ resultsLabel[0]
      }}<VLink :href="source.link" class="!gap-x-1" show-external-icon>{{
        source.name
      }}</VLink
      ><span v-if="resultsLabel[1]">{{ resultsLabel[1] }}</span>
    </p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useUiStore } from "~/stores/ui"
import type { CollectionParams } from "~/types/search"
import { useAnalytics } from "~/composables/use-analytics"

import { useProviderStore } from "~/stores/provider"
import { SupportedMediaType } from "~/constants/media"

import { useI18nResultsCount } from "~/composables/use-i18n-utilities"

import { useMediaStore } from "~/stores/media"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"
import VLink from "~/components/VLink.vue"

const icons = {
  tag: "tag",
  source: "institution",
  creator: "person",
}

/**
 * Renders the header of a tag/creator/source collection page.
 */
export default defineComponent({
  name: "VCollectionHeader",
  components: { VLink, VIcon, VButton },
  props: {
    collectionParams: {
      type: Object as PropType<CollectionParams>,
      required: true,
    },
    creatorUrl: {
      type: String,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const mediaStore = useMediaStore()
    const providerStore = useProviderStore()
    const uiStore = useUiStore()

    const iconName = computed(() => icons[props.collectionParams.collection])
    const collection = computed(() => props.collectionParams.collection)

    const source = computed(() => {
      if (props.collectionParams.collection === "tag") {
        return {
          name: "",
          link: "",
        }
      }
      return {
        name: providerStore.getProviderName(
          props.collectionParams.source,
          props.mediaType
        ),
        link: providerStore.getSourceUrl(
          props.collectionParams.source,
          props.mediaType
        ),
      }
    })

    const title = computed(() => {
      if (props.collectionParams.collection === "tag") {
        return props.collectionParams.tag
      } else if (props.collectionParams.collection === "creator") {
        return props.collectionParams.creator
      }
      return source.value.name
    })

    const url = computed(() => {
      if (props.collectionParams.collection === "tag") {
        return undefined
      } else if (props.collectionParams.collection === "creator") {
        return props.creatorUrl
      }
      return source.value.link
    })
    const { getI18nCollectionResultCountLabel } = useI18nResultsCount()

    const resultsLabel = computed(() => {
      if (mediaStore.resultCount === 0 && mediaStore.fetchState.isFetching) {
        return ""
      }
      const resultsCount = mediaStore.results[props.mediaType].count
      const params =
        props.collectionParams.collection === "creator"
          ? { source: source.value.name }
          : undefined

      const label = getI18nCollectionResultCountLabel(
        resultsCount,
        props.mediaType,
        props.collectionParams.collection,
        params
      )
      if (props.collectionParams.collection === "creator") {
        const splitLabel = label.split(source.value.name)
        return splitLabel.length === 2 ? splitLabel : ["", ""]
      }
      return label
    })

    const isMd = computed(() => uiStore.isBreakpoint("md"))

    const { sendCustomEvent } = useAnalytics()

    const sendAnalyticsEvent = () => {
      if (props.collectionParams.collection === "tag") {
        return
      }

      const eventName =
        props.collectionParams.collection === "creator"
          ? "VISIT_CREATOR_LINK"
          : "VISIT_SOURCE_LINK"
      sendCustomEvent(eventName, {
        url: url.value,
        source: props.collectionParams.source,
      })
    }

    return {
      collection,
      title,
      resultsLabel,
      source,
      url,
      iconName,
      isMd,
      sendAnalyticsEvent,
    }
  },
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.collection-header {
  grid-template-areas: "icon title" "button button" "results results";
}
@screen md {
  .collection-header {
    grid-template-areas: "icon title button" "results results results";
  }
}
.collection-header.tags {
  grid-template-areas: "icon title" "results results";
}
@screen md {
  .collection-header.tags {
    grid-template-areas: "icon title" "results results";
  }
}
.icon {
  grid-area: icon;
}
.title {
  grid-area: title;
}
.button {
  grid-area: button;
}
.results {
  grid-area: results;
}
</style>
