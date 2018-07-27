<template>
<form role="search" method="post" @submit.prevent="onSubmit" class="search-form">
  <div class="search_ctr">
    <input required="required"
           autofocus=""
           class="search_input"
           type="search"
           placeholder="Search the commons..."
           autocapitalize="none"
           id="searchTerm"
           v-model.lazy="form.searchTerm">
    <button class="search_button" title="Search">
    </button>
  </div>
</form>
</template>

<script>
import ImageService from '@/api/ImageService';

export default {
  name: 'search-form',
  data: () => ({ form: { searchTerm: null } }),
  methods: {
    onSubmit(e) {
      e.preventDefault();
      this.getSearchTermResults({ q: this.form.searchTerm });
    },
    getSearchTermResults(searchTerm) {
      ImageService.search(searchTerm);
    },
  },
};
</script>

<style scoped>
.search-form {
  width: 580px;
  max-width: 100%;
  position: relative;
  margin: 0 30px;
}

.search_ctr {
  position: relative;
}

.search_input {
  font-size: 24px;
  padding-left: 30px;
  margin-bottom: 0;
  width: 100%;
  height: 60px;
  box-shadow: 0 1px 2px rgba(0,0,0,.3);
  outline: 0;
  border-radius: 3px;
  border-width: 0;
  background: rgba(255, 255, 255, 0.4);
  color: #fff;
}

.search_input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search_button {
  position: absolute;
  top: 0;
  right: 0;
  background: transparent;
  height: calc( 100% - 3px );
  width: 60px;
  margin: 2px;
  font-size: 24px;
  cursor: pointer;
  transition: all .2s ease-in-out;
  color: #fff;
  border-radius: 3px;
}

.search_button:after {
  content: "";
  background: url('../assets/search-icon.png') center center no-repeat;
  background-size: 20px;
  opacity: 0.5;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  position: absolute;
  z-index: 10;
}
</style>
