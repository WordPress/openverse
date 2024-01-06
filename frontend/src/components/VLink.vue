<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    :aria-disabled="!to"
    v-bind="linkProps"
    :to="to"
    @click="handleClick"
    @mousedown="$emit('mousedown', $event)"
    @blur="$emit('blur', $event)"
    @focus="$emit('focus', $event)"
    @keydown="$emit('keydown', $event)"
  >
    <slot /><VIcon
      v-if="showExternalIcon && !isInternal"
      name="external-link"
      class="inline-block"
      :size="externalIconSize"
      rtl-flip
    />
  </NuxtLink>
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
import { useLocalePath } from "#imports"

import { computed, defineComponent } from "vue"

import { useAnalytics } from "~/composables/use-analytics"

import { defineEvent } from "~/types/emits"

import VIcon from "~/components/VIcon/VIcon.vue"

type ExternalLinkProps = { target: string; rel: string }
type DisabledLinkProps = { role: string }
type LinkProps = ExternalLinkProps | DisabledLinkProps | null

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
  setup(props, { emit }) {
    function checkHref(p: typeof props): p is {
      href: string
      showExternalIcon: boolean
      externalIconSize: number
      sendExternalLinkClickEvent: boolean
      onBlur: (e: FocusEvent) => void
      onFocus: (e: FocusEvent) => void
      onKeydown: (e: KeyboardEvent) => void
      onMousedown: (e: MouseEvent) => void
      onClick: (e: MouseEvent) => void
    } {
      return typeof p.href === "string" && !["", "#"].includes(p.href)
    }
    const localePath = useLocalePath()

    const isInternal = computed(
      () => checkHref(props) && props.href.startsWith("/")
    )
    const linkProps = computed<LinkProps>(() => {
      if (checkHref(props)) {
        if (props.href.startsWith("/")) {
          return null
        } else {
          // External link should open in a new tab
          return { target: "_blank", rel: "noopener noreferrer" }
        }
      }
      // if href is undefined, return props that make the link disabled
      return { role: "link" }
    })
    const to = computed(() => {
      if (checkHref(props)) {
        if (props.href.startsWith("/")) {
          // Internal link should link to the localized page
          return localePath(props.href) ?? props.href
        } else {
          return props.href
        }
      }
      // if href is undefined, return props that make the link disabled
      return undefined
    })

    const { sendCustomEvent } = useAnalytics()

    const handleClick = (e: MouseEvent) => {
      emit("click", e)
      if (
        !checkHref(props) ||
        isInternal.value ||
        !props.sendExternalLinkClickEvent
      ) {
        return
      }
      sendCustomEvent("EXTERNAL_LINK_CLICK", {
        url: props.href,
      })
    }

    return {
      to,
      linkProps,
      isInternal,

      handleClick,
    }
  },
})
</script>
