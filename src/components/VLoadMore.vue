<template>
  <VButton
    size="large"
    variant="full"
    type="button"
    :disabled="isFetching"
    @click="onLoadMore"
  >
    {{ buttonLabel }}
  </VButton>
</template>
<script>
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'
import VButton from '~/components/VButton.vue'
export default defineComponent({
  name: 'VLoadMore',
  components: {
    VButton,
  },
  props: {
    isFetching: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, { emit }) {
    const { i18n } = useContext()

    const buttonLabel = computed(() => {
      return i18n.t('browse-page.load')
    })

    const onLoadMore = () => {
      emit('onLoadMore')
    }

    return {
      buttonLabel,
      onLoadMore,
    }
  },
})
</script>
