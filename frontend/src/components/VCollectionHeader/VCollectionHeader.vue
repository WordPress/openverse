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
      class="results caption-regular md:label-regular mt-2 text-dark-charcoal-70 md:mt-0"
    >
      {{ resultsLabel }}
    </p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useUiStore } from "~/stores/ui"
import type { Collection } from "~/types/search"
import { useAnalytics } from "~/composables/use-analytics"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

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
  components: { VIcon, VButton },
  props: {
    collection: {
      type: String as PropType<Collection>,
      required: true,
    },
    /**
     * The name of the tag/creator/source. The source name should be the display
     * name, not the code.
     */
    title: {
      type: String,
      required: true,
    },
    slug: {
      type: String,
    },
    url: {
      type: String,
    },
    /**
     * The label showing the result count, to display below the title.
     * Should be built by the parent component.
     */
    resultsLabel: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const uiStore = useUiStore()

    const iconName = computed(() => icons[props.collection])

    const isMd = computed(() => uiStore.isBreakpoint("md"))

    const { sendCustomEvent } = useAnalytics()

    const sendAnalyticsEvent = () => {
      if (!props.url || !props.slug) return
      const eventName =
        props.collection === "creator"
          ? "VISIT_CREATOR_LINK"
          : "VISIT_SOURCE_LINK"
      sendCustomEvent(eventName, {
        url: props.url,
        slug: props.slug,
      })
    }

    return {
      iconName,
      isMd,
      sendAnalyticsEvent,
    }
  },
})
</script>

<style scoped>
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
