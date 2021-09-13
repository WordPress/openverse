<template>
  <div class="full-track w-full">
    <div class="waveform h-30">
      <slot name="controller" />
    </div>

    <div class="flex flex-row space-between mx-16 my-6">
      <div class="left-content flex flex-row items-center gap-6">
        <slot name="play-pause" />

        <div class="audio-info">
          <p class="text-3xl font-heading font-semibold">
            {{ audio.title }}
          </p>
          <p class="text-base leading-snug mt-1">{{ audio.creator }}</p>
        </div>
      </div>

      <!-- TODO: Download dropdown -->
      <div class="right-content bg-pink h-12 w-30 rounded-sm ml-auto" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'Full',
  props: ['audio'],
}
</script>
