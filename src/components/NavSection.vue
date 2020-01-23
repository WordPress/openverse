<template>
  <nav class="header nav">
    <a class="logo" href="/">
      <img alt="Logo" src="../assets/cc-search-logo-black.png">
    </a>
    <input class="menu-btn" type="checkbox" id="menu-btn" />
    <label class="menu_icon" for="menu-btn"><span class="navicon"></span></label>
    <ul class="menu">
      <li><a href="/about">About</a></li>
      <li><a href="/collections">Browse by Collection</a></li>
      <li id="search-help"><a href="/search-help">Search Guide</a></li>
      <li><a href="/feedback">Feedback</a></li>
      <li class="nav_search" v-if="showNavSearch ==='true'">
        <form class="hero_search-form"
              role="search"
              method="post"
              v-on:submit.prevent="onSubmit">
          <div class="input-group input-group-rounded">
            <input class="input-group-field"
                  type="search"
                  :placeholder="navSearchPlaceholder"
                  v-model.lazy="form.searchTerm">
            <div class="input-group-button">
              <button type="submit" class="button secondary" value="Search"></button>
            </div>
          </div>
        </form>
      </li>
    </ul>
  </nav>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';

export default {
  props: {
    showNavSearch: {
      default: false,
    },
    navSearchPlaceholder: {
      default: 'Search all images',
    },
  },
  name: 'nav-section',
  data: () => ({ form: { searchTerm: '' } }),
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, { query: { q: this.form.searchTerm }, shouldNavigate: true });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

/* header */

.nav {
  background-image: #fff;
  border-bottom: 1px solid rgba(0,0,0,0.25);
}

.logo > img {
  height: 42px;
  padding-right: 11px;
}

.header {
  box-shadow: 1px 1px 4px 0 rgba(0,0,0,.1);
  width: 100%;
  z-index: 3;
}

.header ul {
  margin: 0;
  padding: 0;
  list-style: none;
  overflow: hidden;
}

li {
  display: block;
  font-family: 'Roboto', sans-serif;
}

.header li a {
  display: block;
  text-decoration: none;
}

.header .logo {
  display: block;
  float: left;
  font-size: 2em;
  padding: 3px 20px;
  text-decoration: none;
}

/* menu */

.header .menu {
  clear: both;
  max-height: 0;
  transition: max-height .2s ease-out;
}

/* menu icon */

.header .menu_icon {
  cursor: pointer;
  float: right;
  padding: 28px 20px;
  position: relative;
  user-select: none;
}

.header .menu_icon .navicon {
  background: #333;
  display: block;
  height: 2px;
  position: relative;
  transition: background .2s ease-out;
  width: 18px;
}

.header .menu_icon .navicon:before,
.header .menu_icon .navicon:after {
  background: #333;
  content: '';
  display: block;
  height: 100%;
  position: absolute;
  transition: all .2s ease-out;
  width: 100%;
}

.header .menu_icon .navicon:before {
  top: 5px;
}

.header .menu_icon .navicon:after {
  top: -5px;
}

/* menu btn */

.header .menu-btn {
  display: none;
}

.header .menu-btn:checked ~ .menu {
  max-height: 240px;
}

.header .menu-btn:checked ~ .menu_icon .navicon {
  background: transparent;
}

.header .menu-btn:checked ~ .menu_icon .navicon:before {
  transform: rotate(-45deg);
}

.header .menu-btn:checked ~ .menu_icon .navicon:after {
  transform: rotate(45deg);
}

.header .menu-btn:checked ~ .menu_icon:not(.steps) .navicon:before,
.header .menu-btn:checked ~ .menu_icon:not(.steps) .navicon:after {
  top: 0;
}

#search-help {
  display: inline-block;
}

/* 48em = 768px */
@media (min-width: 55em) {
  .header {
    height: 3.9em;
  }
  .menu {
    display: inline;
  }
  .header .nav_search {
    float: right;
  }
  .header li {
    display: inline-block;
  }
  .header li a {
    padding: 10px 30px;
  }
  .header .menu_icon {
    display: none;
  }

  #search-help {
    display: none;
  }
}

.menu a {
  color: #333;
  font-size: 1.6em;
  font-weight: 700;
  line-height: 1em;
  margin-top: 0.5rem;
  border-left: 1px solid white;
  border-radius: 2px;
  &:hover {
    background-color: #eee;
  }
}

.hero_search-form {
  margin: 0 15px;
  /* Large and up */
  @media screen and (min-width: 64em) {
    float: right;
  }
  @media screen and (max-width: 70.250em) {
    display: none;
  }
}

.input-group-rounded {
  margin: 9px 0;
  width: 315px;
  max-width: 100%;
  .input-group-field {
    border-radius: 3px;
    padding-left: 1rem;
    background: transparent;
    color: #fff;
    border: 1px solid rgba(36, 36, 36, 0.5);;
    box-shadow: none;
    &:focus {
      border-color: rgb(255, 255, 255);
    }

    &::placeholder {
      color: #1c1c1c;
    }
  }
  .input-group-button .button {
    border-radius: 3px;
    font-size: 0.8rem;
    height: 100%;
    position: relative;
    left: calc( -100% - 10px );
    background: none;
    &:after {
      content: '';
      background: url('../assets/search-icon_black.svg') center center no-repeat;
      background-size: 20px;
      top: 0;
      left: 0;
      bottom: 0;
      right: 0;
      position: absolute;
      z-index: 10;
      opacity: .2;
    }
  }
}
</style>
