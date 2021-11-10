<template>
  <section class="px-10 pb-16">
    <div
      v-if="isForTab == 'all'"
      class="grid gap-4 tab:grid-cols-2 desk:grid-cols-5"
    >
      <VBone v-for="idx in numElems" :key="idx" class="square" />
    </div>

    <div v-if="isForTab == 'image'" class="masonry">
      <VBone
        v-for="idx in numElems"
        :key="idx"
        class="mb-4"
        :style="{ height: `${getRandomSize()}px` }"
      />
    </div>

    <template v-if="isForTab == 'audio'">
      <AudioTrackSkeleton v-for="idx in numElems" :key="idx" />
    </template>
  </section>
</template>

<script>
/**
 * Display placeholder elements while waiting for the actual elements to be
 * loaded in the results views.
 */
export default {
  name: 'GridSkeleton',
  props: {
    isForTab: {
      type: String,
      default: 'image',
      validator: (val) => ['all', 'image', 'audio'].includes(val),
    },
    numElems: {
      type: Number,
      default: function () {
        if (this.isForTab === 'all') return 10
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

<style lang="scss" scoped>
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
