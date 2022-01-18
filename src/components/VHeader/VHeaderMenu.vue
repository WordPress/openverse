<script>
import { inject, onMounted, ref } from '@nuxtjs/composition-api'
import useContentType from '~/composables/use-content-type'

import VMobileContentSwitcher from '~/components/VContentSwitcher/VMobileMenuModal.vue'
import VContentSwitcherPopover from '~/components/VContentSwitcher/VContentSwitcherPopover.vue'
import VDesktopPageMenu from '~/components/VHeader/VPageMenu/VDesktopPageMenu.vue'
import VMobilePageMenu from '~/components/VHeader/VPageMenu/VMobilePageMenu.vue'

export default {
  name: 'VHeaderMenu',
  components: {
    VMobileContentSwitcher,
    VContentSwitcherPopover,
    VDesktopPageMenu,
    VMobilePageMenu,
  },
  props: {
    isSearchRoute: {
      type: Boolean,
      required: true,
    },
  },
  setup() {
    /** @type {import('@nuxtjs/composition-api').Ref<boolean>} */
    const isMinScreenMd = inject('isMinScreenMd')
    /** @type {import('@nuxtjs/composition-api').Ref<null|HTMLElement>} */
    const menuModalRef = ref(null)
    const content = useContentType()

    const isMounted = ref(false)
    onMounted(() => {
      isMounted.value = true
    })
    const selectContentType = (val) => {
      content.setActiveType(val)
      menuModalRef.value?.closeMenu()
    }

    return {
      isMinScreenMd,
      menuModalRef,
      isMounted,

      content,
      selectContentType,
    }
  },
  render(h) {
    if (!this.isSearchRoute) {
      return this.isMinScreenMd && this.isMounted
        ? h(VDesktopPageMenu)
        : h(VMobilePageMenu)
    } else if (this.isMinScreenMd && this.isMounted) {
      return h('div', { class: 'flex flex-grow justify-between' }, [
        h(VDesktopPageMenu),
        h(VContentSwitcherPopover, {
          props: { activeItem: this.content.activeType.value },
          ref: 'menuModalRef',
          on: { select: this.selectContentType },
        }),
      ])
    } else {
      return h(VMobileContentSwitcher, {
        ref: 'menuModalRef',
        props: { activeItem: this.content.activeType.value },
        on: {
          select: this.selectContentType,
        },
      })
    }
  },
}
</script>
