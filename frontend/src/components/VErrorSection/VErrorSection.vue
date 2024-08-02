<script setup lang="ts">
import { defineAsyncComponent } from "#imports"

import { computed } from "vue"

import { ECONNABORTED, NO_RESULT, SERVER_TIMEOUT } from "~/constants/errors"

import type { FetchingError } from "~/types/fetch-state"

const VNoResults = defineAsyncComponent(
  () => import("~/components/VErrorSection/VNoResults.vue")
)
const VErrorImage = defineAsyncComponent(
  () => import("~/components/VErrorSection/VErrorImage.vue")
)

const props = defineProps<{
  fetchingError: FetchingError
}>()

const searchTerm = computed(() => props.fetchingError.details?.searchTerm ?? "")
/**
 * The code used for the error page image.
 * For now, NO_RESULT image is used for searches without result,
 * and SERVER_TIMEOUT image is used as a fall-back for all other errors.
 */
const errorCode = computed(() =>
  props.fetchingError.code === NO_RESULT ? NO_RESULT : SERVER_TIMEOUT
)

const isTimeout = computed(() =>
  [SERVER_TIMEOUT, ECONNABORTED].includes(props.fetchingError.code)
)
</script>

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
