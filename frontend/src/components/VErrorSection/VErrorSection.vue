<template>
  <div class="error-section mx-auto flex max-w-screen-xl flex-row items-center">
    <div class="image-pane hidden max-w-[432px] flex-grow md:block">
      <VErrorImage class="hidden md:block" :error-code="errorCode" />
    </div>
    <div class="flex-grow p-4 md:p-20">
      <VNoResults v-if="errorCode === NO_RESULT" :search-term="searchTerm" />
      <div v-else>
        <h1 class="heading-4 md:heading-2 text-center !font-semibold">
          {{
            isTimeout ? $t("serverTimeout.heading") : $t("unknownError.heading")
          }}
        </h1>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { NO_RESULT, SERVER_TIMEOUT } from "~/constants/errors"
import { useSearchStore } from "~/stores/search"

import type { NuxtError } from "@nuxt/types"

export default defineComponent({
  components: {
    VNoResults: () => import("~/components/VErrorSection/VNoResults.vue"),
    VErrorImage: () => import("~/components/VErrorSection/VErrorImage.vue"),
  },
  props: {
    fetchingError: {
      type: Object as PropType<NuxtError>,
      required: true,
    },
  },
  setup(props) {
    const searchStore = useSearchStore()
    const searchTerm = computed(() => searchStore.searchTerm)
    /**
     * The code used for the error page image.
     * For now, NO_RESULT image is used for searches without result,
     * and SERVER_TIMEOUT image is used as a fall-back for all other errors.
     */
    const errorCode = computed(() => {
      return props.fetchingError?.message?.includes(NO_RESULT)
        ? NO_RESULT
        : SERVER_TIMEOUT
    })

    const isTimeout = computed(() =>
      props.fetchingError?.message?.toLowerCase().includes("timeout")
    )

    return {
      errorCode,
      isTimeout,
      NO_RESULT,
      searchTerm,
    }
  },
})
</script>
