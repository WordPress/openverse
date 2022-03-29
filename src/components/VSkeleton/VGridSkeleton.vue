<template>
  <section>
    <div
      v-if="isForTab === 'all'"
      class="grid gap-4 grid-cols-2 lg:grid-cols-5"
    >
      <VBone v-for="idx in numElems" :key="idx" class="square" />
    </div>

    <div v-if="isForTab === 'image'" class="masonry">
      <VBone
        v-for="idx in numElems"
        :key="idx"
        class="mb-4"
        :style="{ height: `${getRandomSize()}px` }"
      />
    </div>

    <template v-if="isForTab === 'audio'">
      <VAudioTrackSkeleton v-for="idx in numElems" :key="idx" />
    </template>
  </section>
</template>

<script>
/**
 * Display placeholder elements while waiting for the actual elements to be
 * loaded in the results views.
 */
import VAudioTrackSkeleton from '~/components/VSkeleton/VAudioTrackSkeleton.vue'
import VBone from '~/components/VSkeleton/VBone.vue'

export default {
  name: 'VGridSkeleton',
  components: { VAudioTrackSkeleton, VBone },
  props: {
    isForTab: {
      type: String,
      default: 'image',
      validator: (val) => ['all', 'image', 'audio'].includes(val),
    },
    numElems: {
      type: Number,
      default: function () {
        if (this.isForTab === 'all') return 20
        if (this.isForTab === 'image') return 30
        return 8
      },
    },
  },
  setup() {
    function getRandomSize(max = 300, min = 100) {
      return Math.floor(Math.random() * (max - min) + min)
    }

    return { getRandomSize }
  },
}
</script>

<style scoped>
.square {
  aspect-ratio: 1 / 1;
}

.masonry {
  column-count: 2;
  column-gap: 1rem;

  @screen md {
    column-count: 3;
  }

  @screen lg {
    column-count: 5;
  }
}
</style>
