<template>
  <Component :is="linkComponent" v-bind="linkProperties" v-on="$listeners"
    ><slot
  /></Component>
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

const defaultProps = Object.freeze({
  target: '_blank',
  rel: 'noopener noreferrer',
})

export default defineComponent({
  name: 'VLink',
  props: {
    href: {
      type: String,
      required: false,
      validator: (v: string | undefined) =>
        (typeof v === 'string' && v.length > 0) || typeof v === 'undefined',
    },
  },
  setup(props) {
    const { app } = useContext()
    function checkHref(p: typeof props): p is { href: string } {
      return typeof p.href === 'string' && !['', '#'].includes(p.href)
    }

    const hasHref = computed(() => checkHref(props))
    const isInternal = computed(
      () => hasHref.value && props.href?.startsWith('/')
    )
    const linkComponent = computed(() =>
      hasHref.value ? (isInternal.value ? 'NuxtLink' : 'a') : 'span'
    )

    let linkProperties = computed(() =>
      checkHref(props)
        ? isInternal.value
          ? { to: app?.localePath(props.href) ?? props.href }
          : { ...defaultProps, href: props.href }
        : null
    )

    return { linkProperties, linkComponent }
  },
})
</script>
