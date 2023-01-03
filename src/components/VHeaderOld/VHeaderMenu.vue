<script lang="ts">
import { computed, defineComponent, ref } from "@nuxtjs/composition-api"

import useSearchType from "~/composables/use-search-type"
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

    const uiStore = useUiStore()

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    const content = useSearchType()

    /**
     * Clicking on the search type link navigates to the search path,
     * so we only need to close the menu modal here.
     */
    const selectSearchType = () => {
      menuModalRef.value?.closeMenu()
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
