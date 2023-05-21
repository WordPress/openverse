<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    v-if="isNuxtLink"
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    :to="linkTo"
    v-on="$listeners"
    @mousedown.native="$emit('mousedown', $event)"
    @click.native="$emit('click', $event)"
    @blur.native="$emit('blur', $event)"
    @focus.native="$emit('focus', $event)"
    @keydown.native="$emit('keydown', $event)"
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
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    @click="handleExternalClick"
    v-on="$listeners"
  >
    <slot /><VIcon
      v-if="showExternalIcon && !isInternal"
      name="external-link"
      class="inline-block"
      :size="externalIconSize"
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
import { computed, defineComponent } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import { useAnalytics } from "~/composables/use-analytics"

import VIcon from "~/components/VIcon/VIcon.vue"

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
    /**
     * The size of external link icon.
     */
    externalIconSize: {
      type: Number,
      default: 4,
    },
    /**
     * Whether the generic EXTERNAL_LINK_CLICK event should be sent on click.
     */
    sendExternalLinkClickEvent: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const { app } = useContext()
    function checkHref(p: typeof props): p is {
      href: string
      showExternalIcon: boolean
      externalIconSize: number
      sendExternalLinkClickEvent: boolean
    } {
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

    const { sendCustomEvent } = useAnalytics()

    const handleExternalClick = () => {
      if (!checkHref(props) || !props.sendExternalLinkClickEvent) return
      sendCustomEvent("EXTERNAL_LINK_CLICK", {
        url: props.href,
      })
    }

    return {
      linkTo,
      isNuxtLink,
      isInternal,

      handleExternalClick,
    }
  },
})
</script>
