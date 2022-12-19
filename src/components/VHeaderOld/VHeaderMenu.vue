<script lang="ts">
import {
  computed,
  defineComponent,
  ref,
  useRouter,
} from "@nuxtjs/composition-api"

import { ALL_MEDIA, supportedMediaTypes, SearchType } from "~/constants/media"
import useSearchType from "~/composables/use-search-type"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import VMobileMenuModal from "~/components/VContentSwitcherOld/VMobileMenuModal.vue"
import VSearchTypePopoverOld from "~/components/VContentSwitcherOld/VSearchTypePopoverOld.vue"
import VDesktopPageMenu from "~/components/VHeaderOld/VPageMenu/VDesktopPageMenu.vue"
import VMobilePageMenu from "~/components/VHeaderOld/VPageMenu/VMobilePageMenu.vue"

export default defineComponent({
  name: "VHeaderMenu",
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
    const menuModalRef = ref<InstanceType<
      typeof VMobileMenuModal | typeof VSearchTypePopoverOld
    > | null>(null)

    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    const content = useSearchType()

    const selectSearchType = async (type: SearchType) => {
      menuModalRef.value?.closeMenu()
      content.setActiveType(type)

      router.push(searchStore.getSearchPath({ type }))

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
      isDesktopLayout,
      menuModalRef,

      content,
      selectSearchType,
    }
  },
  render(h) {
    if (!this.isSearchRoute) {
      return this.isDesktopLayout ? h(VDesktopPageMenu) : h(VMobilePageMenu)
    } else if (this.isDesktopLayout) {
      return h("div", { class: "flex flex-grow justify-between gap-x-2" }, [
        h(VDesktopPageMenu),
        h(VSearchTypePopoverOld, {
          props: { activeItem: this.content.activeType.value },
          ref: "menuModalRef",
          on: { select: this.selectSearchType },
        }),
      ])
    } else {
      return h(VMobileMenuModal, {
        ref: "menuModalRef",
        props: { activeItem: this.content.activeType.value },
        on: {
          select: this.selectSearchType,
        },
      })
    }
  },
})
</script>
