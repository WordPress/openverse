<script setup lang="ts">
/**
 * This is a wrapper component for all links. If `href` prop is undefined,
 * the link will be rendered as a disabled: an `<a>` element without `href`
 * attribute and with `role="link"` and `aria-disabled="true"` attributes.
 * Links with `href` starting with `/` are treated as internal links.
 *
 * Internal links use `NuxtLink` component with `to` attribute set to `localePath(href)`
 * External links use `a` element, and open in the same tab.
 */
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { useAnalytics } from "~/composables/use-analytics"

import VIcon from "~/components/VIcon/VIcon.vue"

type InternalLinkProps = { to: string }
type ExternalLinkProps = { rel: string }
type DisabledLinkProps = { role: string }
type LinkProps =
  | InternalLinkProps
  | ExternalLinkProps
  | DisabledLinkProps
  | null

const props = withDefaults(
  defineProps<{
    href: string | undefined
    /**
     * whether to render the external link icon next to links that point away
     * from Openverse
     */
    showExternalIcon?: boolean
    externalIconSize?: number
    /**
     * Whether the generic EXTERNAL_LINK_CLICK event should be sent on click.
     * Set to `false` if the link click is tracked by another analytics event.
     */
    sendExternalLinkClickEvent?: boolean
  }>(),
  {
    showExternalIcon: false,
    externalIconSize: 4,
    sendExternalLinkClickEvent: true,
  }
)

const emit = defineEmits<{
  mousedown: [MouseEvent]
  click: [MouseEvent]
  blur: [FocusEvent]
  focus: [FocusEvent]
  keydown: [KeyboardEvent]
}>()

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
const localePath = useNuxtApp().$localePath

const isInternal = computed(
  () => checkHref(props) && props.href.startsWith("/")
)
const linkProps = computed<LinkProps>(() => {
  if (checkHref(props)) {
    if (props.href.startsWith("/")) {
      return null
    } else {
      return { rel: "noopener noreferrer" }
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
</script>

<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    :class="{ 'inline-flex w-max items-center gap-x-2': showExternalIcon }"
    :aria-disabled="!to"
    v-bind="linkProps"
    :to="to"
    @click="handleClick"
    @mousedown="emit('mousedown', $event)"
    @blur="emit('blur', $event)"
    @focus="emit('focus', $event)"
    @keydown="emit('keydown', $event)"
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
