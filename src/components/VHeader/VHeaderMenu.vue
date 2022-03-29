<script>
import {
  inject,
  onMounted,
  ref,
  useContext,
  useRouter,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA, supportedMediaTypes } from '~/constants/media'
import useSearchType from '~/composables/use-search-type'
import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'

import VMobileMenuModal from '~/components/VContentSwitcher/VMobileMenuModal.vue'
import VSearchTypePopover from '~/components/VContentSwitcher/VSearchTypePopover.vue'
import VDesktopPageMenu from '~/components/VHeader/VPageMenu/VDesktopPageMenu.vue'
import VMobilePageMenu from '~/components/VHeader/VPageMenu/VMobilePageMenu.vue'

export default {
  name: 'VHeaderMenu',
  components: {
    VMobileMenuModal,
    VSearchTypePopover,
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
    const content = useSearchType()
    const { app } = useContext()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const router = useRouter()

    const isMounted = ref(false)
    onMounted(() => {
      isMounted.value = true
    })
    const selectSearchType = async (type) => {
      menuModalRef.value?.closeMenu()
      content.setActiveType(type)

      const newPath = app.localePath({
        path: `/search/${type === ALL_MEDIA ? '' : type}`,
        query: searchStore.searchQueryParams,
      })
      router.push(newPath)

      function typeWithoutMedia(mediaType) {
        return mediaStore.resultCountsPerMediaType[mediaType] === 0
      }

      const shouldFetchMedia =
        type === ALL_MEDIA
          ? supportedMediaTypes.every((type) => typeWithoutMedia(type))
          : typeWithoutMedia(type)

      if (shouldFetchMedia) {
        await mediaStore.fetchMedia()
      }
    }

    return {
      isMinScreenMd,
      menuModalRef,
      isMounted,

      content,
      selectSearchType,
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
        h(VSearchTypePopover, {
          props: { activeItem: this.content.activeType.value },
          ref: 'menuModalRef',
          on: { select: this.selectSearchType },
        }),
      ])
    } else {
      return h(VMobileMenuModal, {
        ref: 'menuModalRef',
        props: { activeItem: this.content.activeType.value },
        on: {
          select: this.selectSearchType,
        },
      })
    }
  },
}
</script>
