<template>
  <footer
    ref="footerEl"
    class="footer flex flex-col gap-10 px-6 py-10"
    :class="[
      ...variantNames,
      isContentMode ? 'footer-content' : 'footer-internal',
    ]"
  >
    <!-- Logo and links -->
    <div v-if="isContentMode" class="logo-and-links flex flex-col gap-y-10">
      <VLink href="/" class="logo text-dark-charcoal">
        <VBrand class="text-[18px]" />
      </VLink>
      <nav>
        <VPageLinks
          class="nav-list label-regular"
          :style="linkColumnHeight"
          nav-link-classes="py-2"
        />
      </nav>
    </div>

    <!-- Locale chooser and WordPress affiliation graphic -->
    <div class="locale-and-wp flex flex-col justify-between gap-y-10">
      <VLanguageSelect v-bind="languageProps" class="language max-w-full" />
      <VWordPressLink mode="light" />
    </div>
  </footer>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from "@nuxtjs/composition-api"

import { CSSProperties } from "@vue/runtime-dom"

import usePages from "~/composables/use-pages"
import useResizeObserver from "~/composables/use-resize-observer"

import { SCREEN_SIZES } from "~/constants/screens"

import { useUiStore } from "~/stores/ui"

import type { SelectFieldProps } from "~/components/VSelectField/VSelectField.vue"
import VLink from "~/components/VLink.vue"
import VBrand from "~/components/VBrand/VBrand.vue"
import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"
import VPageLinks from "~/components/VHeader/VPageLinks.vue"
import VWordPressLink from "~/components/VHeader/VWordPressLink.vue"

/**
 * The footer is the section displayed at the bottom of a page. It can contain
 * some branding, links to other pages and an option to change the language.
 */
export default defineComponent({
  name: "VFooter",
  components: {
    VWordPressLink,
    VPageLinks,
    VLanguageSelect,
    VLink,
    VBrand,
  },
  props: {
    /**
     * whether the footer is being rendered on a content page or an internal
     * page; This determines whether the Openverse logo and other links are
     * displayed.
     */
    mode: {
      type: String as PropType<"internal" | "content">,
      required: false,
    },
    languageProps: {
      type: Object as PropType<SelectFieldProps>,
      default: () => ({}),
    },
  },
  setup(props) {
    const uiStore = useUiStore()
    const { all: allPages, current: currentPage } = usePages(true)

    const isContentMode = computed(() => props.mode === "content")

    /** JS-based responsiveness */
    const footerEl = ref<HTMLElement | null>(null)
    const initialWidth = SCREEN_SIZES[uiStore.breakpoint]
    const { dimens: footerDimens } = useResizeObserver(footerEl, {
      initialWidth,
    })

    /**
     * Return a list of all breakpoints that are smaller than the current screen width. This allows us to use the smallest variant class to target CSS styles.
     *
     * I.e., with a width at 1200, the footer will have `footer-2xl footer-lg`. Using `footer-lg`, we can apply styles to both `footer-2xl` and `footer-lg`.
     */
    const variantNames = computed(() =>
      Object.entries(SCREEN_SIZES)
        .filter(([, val]) => footerDimens.value.width >= val)
        .map(([key]) => `footer-${key}`)
    )

    const linkColumnHeight = computed<CSSProperties>(() => ({
      "--link-col-height": Math.ceil(Object.keys(allPages).length / 2),
    }))

    return {
      isContentMode,
      allPages,
      currentPage,

      footerEl,
      variantNames,
      linkColumnHeight,
    }
  },
})
</script>

<style>
/* wrapper element styles */
.footer-sm {
  @apply px-6;
}
.footer-lg {
  @apply gap-y-8 px-10;
}
.footer-internal {
  @apply pt-6;
}
.footer-internal.footer-lg {
  @apply pt-10;
}

/* footer > logo-and-links styles */
.footer-sm .logo-and-links {
  @apply grid grid-flow-col grid-cols-2;
}

.footer-lg .logo-and-links {
  @apply flex flex-row items-center justify-between;
}

/* logo-and-links > nav-list styles */

.nav-list {
  @apply grid grid-flow-col grid-cols-2 items-center gap-y-2 gap-x-10;
  /*
  We set the number of rows in JS to have 2 equally distributed link columns.
  */
  grid-template-rows: repeat(var(--link-col-height, 3), auto);
}

.footer-lg .nav-list {
  @apply flex gap-x-6;
}

/* locale-and-wp locale chooser and WordPress affiliation graphic styles */
.footer-content.footer-sm .locale-and-wp {
  @apply grid grid-cols-2 items-center;
}
.footer-content.footer-lg .locale-and-wp,
.footer-internal.footer-sm .locale-and-wp {
  @apply flex flex-row items-center justify-between;
}

/* element styles */
.footer-sm .logo {
  @apply self-start pt-2;
}
.footer .language {
  width: 100% !important;
}
.footer-sm .language {
  @apply max-w-[12.5rem];
}
</style>
