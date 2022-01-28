<script>
import {
  inject,
  onMounted,
  ref,
  useContext,
  useRouter,
  useStore,
} from '@nuxtjs/composition-api'
import useContentType from '~/composables/use-content-type'

import VMobileMenuModal from '~/components/VContentSwitcher/VMobileMenuModal.vue'
import VContentSwitcherPopover from '~/components/VContentSwitcher/VContentSwitcherPopover.vue'
import VDesktopPageMenu from '~/components/VHeader/VPageMenu/VDesktopPageMenu.vue'
import VMobilePageMenu from '~/components/VHeader/VPageMenu/VMobilePageMenu.vue'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { FETCH_MEDIA } from '~/constants/action-types'
import { MEDIA } from '~/constants/store-modules'
import isEmpty from 'lodash.isempty'

export default {
  name: 'VHeaderMenu',
  components: {
    VMobileMenuModal,
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
    const { app } = useContext()
    const store = useStore()
    const router = useRouter()

    const isMounted = ref(false)
    onMounted(() => {
      isMounted.value = true
    })
    const selectContentType = async (type) => {
      menuModalRef.value?.closeMenu()
      await content.setActiveType(type)

      const newPath = app.localePath({
        path: `/search/${type === ALL_MEDIA ? '' : type}`,
        query: store.getters['search/searchQueryParams'],
      })
      router.push(newPath)

      function typeWithoutMedia(mediaType) {
        return isEmpty(store.getters['media/mediaResults'][mediaType])
      }

      const shouldFetchMedia =
        type === ALL_MEDIA
          ? [AUDIO, IMAGE].every((type) => typeWithoutMedia(type))
          : typeWithoutMedia(type)

      if (shouldFetchMedia) {
        await store.dispatch(`${MEDIA}/${FETCH_MEDIA}`, {
          ...store.getters['search/searchQueryParams'],
        })
      }
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
      return h('div', { class: 'flex flex-grow justify-between gap-x-2' }, [
        h(VDesktopPageMenu),
        h(VContentSwitcherPopover, {
          props: { activeItem: this.content.activeType.value },
          ref: 'menuModalRef',
          on: { select: this.selectContentType },
        }),
      ])
    } else {
      return h(VMobileMenuModal, {
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
