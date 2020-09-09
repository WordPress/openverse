<template>
  <button
    v-if="showBtn"
    :aria-label="$t('browse-page.aria.scroll')"
    class="scroll"
    @click="scrollToTop"
    @keyup.enter="scrollToTop"
  >
    <i>
      <svg
        width="20"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        height="20"
        viewBox="0 0 64 64"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        enable-background="new 0 0 64 64"
      >
        <g>
          <path
            fill="#fff"
            d="M3.352,48.296l28.56-28.328l28.58,28.347c0.397,
              0.394,0.917,0.59,1.436,0.59c0.52,0,1.04-0.196,
              1.436-0.59   c0.793-0.787,0.793-2.062,
              0-2.849l-29.98-29.735c-0.2-0.2-0.494-0.375-0.757-0.475c-0.75-0.282-1.597-0.107-2.166,
              0.456   L0.479,45.447c-0.793,0.787-0.793,2.062,
              0,2.849C1.273,49.082,2.558,
              49.082,3.352,48.296z"
          />
        </g>
      </svg>
    </i>
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
