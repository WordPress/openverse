<template>
<form role="search" method="post" @submit.prevent="onSubmit" class="search-form">
  <div class="search_ctr">
    <input required="required"
           autofocus=""
           class="search_input"
           type="search"
           placeholder="Search for photos…"
           autocapitalize="none"
           id="searchTerm"
           v-model.lazy="form.searchTerm">
    <button class="search_button" title="Search">
      Search
    </button>
  </div>
</form>
</template>

<script>
import ImageService from '@/api/ImageService';
import EventBus from '@/api/EventBus';

export default {
  name: 'search-form',
  data: () => ({ form: { searchTerm: null } }),
  methods: {
    onSubmit(e) {
      e.preventDefault();
      this.getSearchTermResults({ q: this.form.searchTerm });
    },
    getSearchTermResults(searchTerm) {
      ImageService.search(searchTerm)
        .then(results => EventBus.$emit('search-form:getSearchTermResults', searchTerm));
    },
  },
};
</script>

<style scoped>
.search-form {
  width: 580px;
  position: relative;
}

.search_ctr {
  position: relative;
}

.search_input {
  font-size: 18px;
  padding: 16px 18px;
  margin-bottom: 0;
  width: 100%;
  box-shadow: 0 1px 2px rgba(0,0,0,.3);
  outline: 0;
  border-radius: 3px;
  border-width: 0;
}

.search_button {
  position: absolute;
  top: 0;
  right: 0;
  background: #4a90e2;
  height: calc( 100% - 3px );
  width: 20%;
  border-radius: 3px;
  border: 1px solid #2275d7;
  margin:2px;
  font-size: 24px;
  cursor: pointer;
  transition: all .2s ease-in-out;
  color: #fff;
}
</style>
