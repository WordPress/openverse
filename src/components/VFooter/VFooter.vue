<template>
  <footer
    ref="footerEl"
    class="footer flex flex-col gap-10 px-6 py-10"
    :class="variantNames"
  >
    <!-- Logo and links -->
    <div v-if="isContentMode" class="logo-and-links flex flex-col gap-10">
      <VLink href="/" class="text-dark-charcoal">
        <VBrand class="text-[18px]" />
      </VLink>
      <nav>
        <ul class="nav-list grid grid-cols-2 gap-6 text-sm">
          <li v-for="page in allPages" :key="page.id">
            <VLink
              class="text-dark-charcoal"
              :href="page.link"
              show-external-icon
              >{{ $t(`navigation.${page.id}`) }}</VLink
            >
          </li>
        </ul>
      </nav>
    </div>

    <!-- Locale chooser and WordPress affiliation graphic -->
    <div class="locale-and-wp flex flex-col justify-between gap-10">
      <div
        class="language flex h-10 w-full w-full items-center justify-center rounded-sm border border-dark-charcoal-20 bg-white"
      >
        {{ $t('footer.wip') }}
      </div>
      <VLink
        href="https://wordpress.org"
        class="text-dark-charcoal hover:no-underline"
      >
        <i18n
          tag="div"
          path="footer.wordpress-affiliation"
          class="flex h-full flex-row items-center gap-2 text-sm"
        >
          <template #wordpress>
            <WordPress class="aria-hidden" />
            <span class="sr-only">WordPress</span>
          </template>
        </i18n>
      </VLink>
    </div>
  </footer>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'

import useResizeObserver from '~/composables/use-resize-observer'

import { SCREEN_SIZES } from '~/constants/screens'

import VLink from '~/components/VLink.vue'
import VBrand from '~/components/VBrand/VBrand.vue'

import WordPress from '~/assets/wordpress.svg?inline'

/**
 * The footer is the section displayed at the bottom of a page. It can contain
 * some branding, links to other pages and an option to change the language.
 */
export default defineComponent({
  name: 'VFooter',
  components: {
    VLink,
    VBrand,
    WordPress,
  },
  props: {
    /**
     * whether the footer is being rendered on a content page or an internal
     * page; This determines whether the Openverse logo and other links are
     * displayed.
     */
    mode: {
      type: String as PropType<'internal' | 'content'>,
      required: false,
      default: undefined,
    },
  },
  setup(props) {
    const { all: allPages, current: currentPage } = usePages(true)

    const isContentMode = computed(() => {
      if (props.mode) {
        return props.mode === 'content'
      } else {
        return ['search', 'audio', 'image'].some((prefix) =>
          currentPage.value?.startsWith(prefix)
        )
      }
    })

    /** JS-based responsiveness */
    const footerEl = ref<HTMLElement | null>(null)
    const { dimens: footerDimens } = useResizeObserver(footerEl)
    const variantNames = computed(() =>
      Array.from(SCREEN_SIZES)
        .filter(([, val]) => footerDimens.value.width >= val)
        .map(([key]) => `footer-${key}`)
    )

    return {
      isContentMode,
      allPages,

      footerEl,
      variantNames,
    }
  },
})
</script>

<style>
.footer.footer-sm .nav-list {
  @apply flex flex-row gap-8;
}

.footer.footer-sm .locale-and-wp {
  @apply flex-row;
}

.footer.footer-sm .language {
  @apply w-50;
}

.footer.footer-md .logo-and-links {
  @apply flex-row items-center justify-between;
}

.footer.footer-lg {
  @apply px-10;
}

.footer.footer-xl {
  @apply flex-row gap-8;
}

.footer.footer-xl .logo-and-links {
  @apply flex-grow;
}

.footer.footer-xl .locale-and-wp {
  @apply flex-grow;
}
</style>
