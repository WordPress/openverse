<template>
  <div
    class="flex gap-2"
    role="radiogroup"
    :aria-label="$t('hero.aria.search-type')"
  >
    <button
      class="toggle-button"
      role="radio"
      type="button"
      :aria-checked="value === 'all'"
      @click="$emit('selected', 'image')"
    >
      {{ $t('hero.search-type.all') }}
    </button>
    <button
      class="toggle-button"
      role="radio"
      type="button"
      :aria-checked="value === 'image'"
      @click="$emit('selected', 'image')"
    >
      {{ $t('hero.search-type.image') }}
    </button>
    <button
      class="toggle-button"
      role="radio"
      type="button"
      :aria-checked="value === 'audio'"
      @click="$emit('selected', 'audio')"
    >
      {{ $t('hero.search-type.audio') }}
    </button>
  </div>
</template>

<script>
export default {
  model: {
    prop: 'value',
    event: 'selected',
  },
  props: {
    value: {
      type: String,
      default: 'image',
    },
  },
}
</script>

<style scoped>
.toggle-button {
  @apply py-2 px-4 font-semibold border-2 rounded-sm border-gray;
}

.toggle-button[aria-checked='true'] {
  @apply bg-trans-blue text-white border-trans-blue;
}
</style>
