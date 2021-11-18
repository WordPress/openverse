<template>
  <button
    v-if="showBtn"
    :aria-label="$t('browse-page.aria.scroll')"
    class="scroll text-white bg-trans-blue hover:bg-trans-blue-action transition-all duration-100 ease-linear fixed end-4 bottom-4 w-14 h-14 hover:shadow-md rounded-full text-center"
    @click="scrollToTop"
    @keyup.enter="scrollToTop"
  >
    <svg
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-hidden="true"
      focusable="false"
      class="w-full h-full fill-curr"
    >
      <path d="M6.5 12.4L12 8l5.5 4.4-.9 1.2L12 10l-4.5 3.6-1-1.2z" />
    </svg>
  </button>
</template>

<script>
export default {
  name: 'ScrollButton',
  props: {
    showBtn: {
      type: Boolean,
    },
  },
  methods: {
    scrollToTop() {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth',
      })
    },
  },
}
</script>
