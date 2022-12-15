<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    v-if="isNuxtLink"
    :class="{ 'inline-flex flex-row items-center gap-2': showExternalIcon }"
    :to="linkTo"
    v-on="$listeners"
    @click.native="$emit('click', $event)"
  >
    <slot />
  </NuxtLink>
  <a
    v-else
    :href="href"
    target="_blank"
    rel="noopener noreferrer"
    :role="href ? undefined : 'link'"
    :aria-disabled="!href"
    :class="{ 'inline-flex flex-row items-center gap-2': showExternalIcon }"
    v-on="$listeners"
  >
    <slot /><VIcon
      v-if="showExternalIcon && !isInternal"
      :icon-path="externalLinkIcon"
      class="inline-block"
      :size="4"
      rtl-flip
    />
  </a>
</template>

<script lang="ts">
/**
 * This is a wrapper component for all links. If `href` prop is undefined,
 * the link will be rendered as a disabled: an `<a>` element without `href`
 * attribute and with `role="link"` and `aria-disabled="true"` attributes.
 * Links with `href` starting with `/` are treated as internal links.
 *
 * Internal links use `NuxtLink` component with `to` attribute set to `localePath(href)`
 * External links use `a` element set to open in a new tab and not raise an error with the current iframe setup.
 */
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api"

import VIcon from "~/components/VIcon/VIcon.vue"

import externalLinkIcon from "~/assets/icons/external-link.svg"

export default defineComponent({
  name: "VLink",
  components: { VIcon },
  props: {
    href: {
      type: String,
      required: false,
      validator: (v: string | undefined) =>
        (typeof v === "string" && v.length > 0) || typeof v === "undefined",
    },
    /**
     * whether to render the external link icon next to links that point away
     * from Openverse
     */
    showExternalIcon: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { app } = useContext()
    function checkHref(
      p: typeof props
    ): p is { href: string; showExternalIcon: boolean } {
      return typeof p.href === "string" && !["", "#"].includes(p.href)
    }

    const hasHref = computed(() => checkHref(props))
    const isInternal = computed(
      () => hasHref.value && props.href?.startsWith("/")
    )
    const isNuxtLink = computed(() => hasHref.value && isInternal.value)

    let linkTo = computed(() =>
      checkHref(props) && isInternal.value
        ? app?.localePath(props.href) ?? props.href
        : null
    )

    return {
      linkTo,
      isNuxtLink,
      isInternal,
      externalLinkIcon,
    }
  },
})
</script>
