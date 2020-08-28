<template>
  <div class="app">
    <HeaderSection />
    <main role="main">
      <Nuxt />
    </main>
    <FooterSection />
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}
</style>

<style lang="scss">
@import '@creativecommons/vocabulary/scss/vocabulary.scss';

body {
  margin: 0;
  font-family: 'Source Sans Pro', sans-serif;
  font-display: swap;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333333;
}

.full-height-sticky {
  @include desktop {
    z-index: 20;
    height: 100vh;
    position: sticky;
    top: 0;
  }
}

// override global header styles for now
.cc-global-header .container {
  max-width: 100%;
}

/**
* Arrow popup styles
* @todo: Move when this is made into a proper component
*/
// from http://www.cssarrowplease.com/
.arrow-popup {
  position: absolute;
  background: #ffffff;
  border: 2px solid #d8d8d8;
  z-index: 10;
  width: 22rem;
}

@include desktop {
  .arrow-popup.arrow-popup--anchor-right {
    right: 0;
    top: 100%;
    display: block;
  }
}

.arrow-popup:after,
.arrow-popup:before {
  bottom: 100%;
  left: 10%;
  border: solid transparent;
  content: ' ';
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}

.arrow-popup:after {
  border-color: rgba(255, 255, 255, 0);
  border-bottom-color: #ffffff;
  border-width: 10px;
  margin-left: -10px;
}
.arrow-popup:before {
  border-color: rgba(120, 120, 120, 0);
  border-bottom-color: #d8d8d8;
  border-width: 13px;
  margin-left: -13px;
}

@include desktop {
  .arrow-popup--anchor-right.arrow-popup:after {
    left: auto;
    right: 10%;
    margin-left: auto;
    margin-right: -10px;
  }
  .arrow-popup--anchor-right.arrow-popup:before {
    left: auto;
    right: 10%;
    margin-left: auto;
    margin-right: -13px;
  }
}
</style>
