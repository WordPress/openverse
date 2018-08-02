<template>
<form role="search"
      method="post"
      @submit.prevent="onSubmit"
      class="search-form search-form__filter">
  <div class="search-form_ctr grid-x global-nav show-for-smedium">
      <div class="search-form_inner-ctr medium-6 large-9">
        <input required="required"
               autofocus=""
               class="search-form_input"
               type="search"
               placeholder="Search the commons..."
               autocapitalize="none"
               id="searchInput"
               v-model="query">
        <ul class="search-form_toolbar menu" role="menubar">
          <li class="menu-button" role="menuitem">
            <a @click.prevent="onSubmit"
               href="https://foundation.zurb.com/develop/getting-started.html"
               class="button">Search</a>
          </li>
          <li class="menu-button" role="menuitem">
            <a href="https://foundation.zurb.com/develop/getting-started.html"
               class="button">Filter</a>
          </li>
        </ul>
      </div>
  </div>
</form>
</template>

<script>
import { FETCH_IMAGES } from '@/store/action-types';


export default {
  name: 'search-form',
  data: () => ({ query: null }),
  methods: {
    onSubmit(e) {
      e.preventDefault();
      if (this.query) {
        this.$store.dispatch(FETCH_IMAGES, { q: this.query });
      }
    },
  },
  mounted() {
    this.query = this.$store.state.query.q;
  },
};
</script>

<style lang="scss" scoped>
.search-form {
  width: 580px;
  max-width: 100%;
  position: relative;
  margin: 0 30px;
}

.search-form_ctr {
  position: relative;
  height: 70px;
}

.search-form_input {
  font-size: 24px;
  padding-left: 30px;
  margin-bottom: 0;
  width: 600px;
  height: 60px;
  outline: 0;
  border-radius: 3px;
  border-width: 0;
  color: #000;
}

.search-form_inner-ctr {
  display: flex;
}

.search-form__filter {
  width: 100%;
  border-bottom: 1px solid #e6e6e6;

  .search-form_input {
    width: 100%;
    height: 100%;
    outline: 0;
    border-radius: 0;
    border-width:  0;
    color: #000;
  }
}


.search-form_input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-form_toolbar {
  width: 400px;


  li {
    display: flex;
    flex: 0 0 auto;
    border-left: 1px solid #e6e6e6;
    border-right: 1px solid #e6e6e6;
  }

  .menu-button {
    height: 100%;
    margin: 0;
    color: #000;

  }
}
</style>
