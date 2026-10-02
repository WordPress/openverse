<script setup lang="ts">
/**
 * The footer is the section displayed at the bottom of a page. It can contain
 * some branding, links to other pages and an option to change the language.
 */
import { computed } from "vue"

import usePages from "~/composables/use-pages"

import type { SelectFieldProps } from "~/components/VSelectField/VSelectField.vue"
import VLink from "~/components/VLink.vue"
import VBrand from "~/components/VBrand/VBrand.vue"
import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"
import VThemeSelect from "~/components/VThemeSelect/VThemeSelect.vue"
import VPageLinks from "~/components/VHeader/VPageLinks.vue"
import VWordPressLink from "~/components/VHeader/VWordPressLink.vue"

type FooterMode = "internal" | "content"

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    /**
     * whether the footer is being rendered on a search page or an internal
     * page (about, feedback, etc.); This determines whether the Openverse
     * logo and other links are displayed.
     * Search pages use "content" footer.
     */
    mode: FooterMode
    languageProps?: SelectFieldProps
  }>(),
  {
    languageProps: () => ({}),
  }
)

const { all: allPages } = usePages()

const isContentMode = computed(() => props.mode === "content")

const linkColumnHeight = computed(() => ({
  "--link-col-height": Math.ceil(Object.keys(allPages).length / 2),
}))
</script>

<template>
  <div class="footer-container">
    <footer
      v-bind="$attrs"
      class="footer flex flex-col gap-10 px-6"
      :class="isContentMode ? 'footer-content' : 'footer-internal'"
    >
      <!-- Logo and links -->
      <div v-if="isContentMode" class="logo-and-links flex flex-col gap-y-10">
        <VLink href="/" class="logo text-default" aria-label="Openverse">
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

      <!-- Locale chooser, theme chooser, and WordPress affiliation graphic -->
      <div class="locale-and-wp flex flex-col justify-between">
        <VWordPressLink />
        <div class="flex flex-row items-center gap-6">
          <VLanguageSelect
            v-bind="languageProps"
            class="language max-w-full border-secondary"
          />
          <VThemeSelect class="border-secondary" />
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
.footer-container {
  container-type: inline-size;
}

.footer-internal {
  @apply py-6;
}

.footer-content {
  @apply py-10;
}

.nav-list {
  @apply grid grid-flow-col grid-cols-2 items-center gap-x-10 gap-y-2;
  /*
  We set the number of rows in JS to have 2 equally distributed link columns.
  */
  grid-template-rows: repeat(var(--link-col-height, 4), auto);
}

.footer-content .locale-and-wp {
  @apply gap-y-10;
}

.footer-internal .locale-and-wp {
  @apply gap-y-4;
}

.footer .language {
  width: 100% !important;
}

@container (min-width: 640px) {
  .footer .logo-and-links {
    @apply grid grid-flow-col grid-cols-2;
  }

  .footer-content .locale-and-wp {
    @apply grid grid-cols-2 items-center;
  }

  .footer-internal .locale-and-wp {
    @apply flex flex-row items-center;
  }

  .footer .logo {
    @apply self-start pt-2;
  }

  .footer .language {
    @apply max-w-[12.5rem];
  }
}

@container (min-width: 1024px) {
  .footer {
    @apply gap-y-8 px-10;
  }

  .footer .logo-and-links {
    @apply flex flex-row items-center justify-between;
  }

  .footer .nav-list {
    @apply flex gap-x-6;
  }

  .footer-content .locale-and-wp {
    @apply flex flex-row items-center;
  }
}
</style>
