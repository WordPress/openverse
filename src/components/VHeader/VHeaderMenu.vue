<script>
import {
  inject,
  onMounted,
  ref,
  useContext,
  useRouter,
  useStore,
} from '@nuxtjs/composition-api'
import isEmpty from 'lodash.isempty'

import useSearchType from '~/composables/use-search-type'

import { ALL_MEDIA, supportedMediaTypes } from '~/constants/media'
import { FETCH_MEDIA } from '~/constants/action-types'
import { MEDIA } from '~/constants/store-modules'

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
    const store = useStore()
    const router = useRouter()

    const isMounted = ref(false)
    onMounted(() => {
      isMounted.value = true
    })
    const selectSearchType = async (type) => {
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
          ? supportedMediaTypes.every((type) => typeWithoutMedia(type))
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
