<template>
  <button
    v-if="showBtn"
    :aria-label="$t('browse-page.aria.scroll')"
    class="scroll"
    @click="scrollToTop"
    @keyup.enter="scrollToTop"
  >
    <svg
      width="20"
      xmlns="http://www.w3.org/2000/svg"
      height="20"
      viewBox="0 0 64 64"
    >
      <path
        fill="#fff"
        d="M3.352 48.296l28.56-28.328 28.58 28.347c.397.394.917.59 1.436.59.52 0 1.04-.196 1.436-.59a2.003 2.003 0 000-2.849l-29.98-29.735c-.2-.2-.494-.375-.757-.475a2.052 2.052 0 00-2.166.456L.479 45.447a2.003 2.003 0 000 2.849 2.045 2.045 0 002.873 0z"
      />
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
      /* istanbul ignore next */
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth',
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.scroll {
  right: 10px;
  width: 50px;
  height: 50px;
  position: fixed;
  bottom: 10px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.25);
  background-color: #5fd1fc;
  color: #fff;
  border-radius: 50%;
  outline: none;
  cursor: pointer;
  transition: all 5s ease-in;
  z-index: 5;
}

.scroll:hover {
  background-color: #1e96c2;
}
</style>
