<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    v-if="isInternal"
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    v-bind="{ ...linkProps, ...$attrs }"
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
    v-bind="{ ...linkProps, ...$attrs }"
    :aria-disabled="!href"
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    @click="handleExternalClick"
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
 * External links use `a` element. If `href` does not start with `#`, they are set to
 * open in a new tab.
 */
import { computed, defineComponent } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import { useAnalytics } from "~/composables/use-analytics"

import { defineEvent } from "~/types/emits"

import VIcon from "~/components/VIcon/VIcon.vue"

type InternalLinkProps = { to: string }
type ExternalLinkProps = { target: string; rel: string }
type DisabledLinkProps = { role: string }
type LinkProps =
  | InternalLinkProps
  | ExternalLinkProps
  | DisabledLinkProps
  | null

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
     * Set to `false` if the link click is tracked by another analytics event.
     */
    sendExternalLinkClickEvent: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    mousedown: defineEvent<[MouseEvent]>(),
    click: defineEvent<[MouseEvent]>(),
    blur: defineEvent<[FocusEvent]>(),
    focus: defineEvent<[FocusEvent]>(),
    keydown: defineEvent<[KeyboardEvent]>(),
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

    const linkProps = computed<LinkProps>(() => {
      if (checkHref(props)) {
        if (props.href?.startsWith("/")) {
          // Internal link should link to the localized page
          return { to: app?.localePath(props.href) ?? props.href }
        } else if (props.href?.startsWith("#")) {
          // Anchor link for skip-to-content button
          return null
        } else {
          // External link should open in a new tab
          return { target: "_blank", rel: "noopener noreferrer" }
        }
      }
      // if href is undefined, return props that make the link disabled
      return { role: "link" }
    })

    const { sendCustomEvent } = useAnalytics()

    const handleExternalClick = () => {
      if (!checkHref(props) || !props.sendExternalLinkClickEvent) {
        return
      }
      sendCustomEvent("EXTERNAL_LINK_CLICK", {
        url: props.href,
      })
    }

    return {
      linkProps,
      isInternal,

      handleExternalClick,
    }
  },
})
</script>
