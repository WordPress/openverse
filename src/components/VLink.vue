<!-- eslint-disable vue/no-restricted-syntax -->
<template>
  <NuxtLink
    v-if="linkComponent === 'NuxtLink'"
    v-bind="$attrs"
    :class="{ 'inline-flex flex-row items-center gap-2': showExternalIcon }"
    :to="linkTo"
    v-on="$listeners"
    @click.native="$emit('click', $event)"
  >
    <slot /><VIcon
      v-if="showExternalIcon && !isInternal"
      :icon-path="externalLinkIcon"
      class="inline-block"
      :size="4"
      rtl-flip
    />
  </NuxtLink>
  <a
    v-else-if="linkComponent === 'a'"
    v-bind="$attrs"
    :href="href"
    target="_blank"
    rel="noopener noreferrer"
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
  <span
    v-else
    v-bind="$attrs"
    :class="{ 'inline-flex flex-row items-center gap-2': showExternalIcon }"
  >
    <slot /><VIcon
      v-if="showExternalIcon && !isInternal"
      :icon-path="externalLinkIcon"
      class="inline-block"
      :size="4"
      rtl-flip
    />
  </span>
</template>

<script lang="ts">
/**
 * This is a wrapper component for all links. If a link is dynamically generated and doesn't have
 * an `href` prop (as the links for detail pages when the image detail hasn't loaded yet),
 * it is rendered as a `span`.
 * Links with `href` starting with `/` are treated as internal links.
 *
 * Internal links use `NuxtLink` component with `to` attribute set to `localePath(href)`
 * External links use `a` element set to open in a new tab and not raise an error with the current iframe setup.
 */
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'

export default defineComponent({
  name: 'VLink',
  components: { VIcon },
  inheritAttrs: false,
  props: {
    href: {
      type: String,
      required: false,
      validator: (v: string | undefined) =>
        (typeof v === 'string' && v.length > 0) || typeof v === 'undefined',
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
      return typeof p.href === 'string' && !['', '#'].includes(p.href)
    }

    const hasHref = computed(() => checkHref(props))
    const isInternal = computed(
      () => hasHref.value && props.href?.startsWith('/')
    )
    const linkComponent = computed(() =>
      hasHref.value ? (isInternal.value ? 'NuxtLink' : 'a') : 'span'
    )

    let linkTo = computed(() =>
      checkHref(props) && isInternal.value
        ? app?.localePath(props.href) ?? props.href
        : null
    )

    return {
      linkTo,
      linkComponent,
      isInternal,
      externalLinkIcon,
    }
  },
})
</script>
