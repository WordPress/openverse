<script lang="ts">
import {
  ComponentInstance,
  defineComponent,
  inject,
  onMounted,
  Ref,
  ref,
  useContext,
  useRouter,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA, searchPath, supportedMediaTypes } from '~/constants/media'
import useSearchType from '~/composables/use-search-type'
import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'

import VMobileMenuModal from '~/components/VContentSwitcherOld/VMobileMenuModal.vue'
import VSearchTypePopoverOld from '~/components/VContentSwitcherOld/VSearchTypePopoverOld.vue'
import VDesktopPageMenu from '~/components/VHeaderOld/VPageMenu/VDesktopPageMenu.vue'
import VMobilePageMenu from '~/components/VHeaderOld/VPageMenu/VMobilePageMenu.vue'

export default defineComponent({
  name: 'VHeaderMenu',
  components: {
    VMobileMenuModal,
    VSearchTypePopoverOld,
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
    const isMinScreenMd: Ref<boolean> = inject('isMinScreenMd')
    const menuModalRef = ref<ComponentInstance | null>(null)
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
        path: searchPath(type),
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
        h(VSearchTypePopoverOld, {
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
})
</script>
