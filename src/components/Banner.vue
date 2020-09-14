<template>
  <section class="section">
    <div class="banner_two" v-bind:class="{'change':task.id}">
      <div class="columns">
        <section class="column section is-8">
          <p class="margin-top-normal">
            If you donate $5 today, and everyone else does the same,
            we can keep growing our database of freely reusable content. For you. For all of us.
          </p>
        </section>
        <section class="column section">
          <button type="submit" class="donate button is-small" v-on:click="redirect">
            <i class="icon cc-letterheart-filled margin-right-small is-size-5 padding-top-smaller" />Yes, I’ll donate now
          </button>
        </section>
        <section class="column section">
          <button class="label_two button is-small" v-on:click="onclick">Not today</button>
        </section>
        <section class="column section">
          <button class="button_two button" v-on:click="onclick">x</button>
        </section>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'Banner',
  methods: {
    onclick() {
      this.task.id = true
    },
    redirect() {
      window.location.href =
        'https://www.classy.org/give/297881/#!/donation/checkout'
    },
  },
  data() {
    return {
      task: {
        id: false,
      },
    }
  },
}
</script>



<style scoped>
.change {
  display: none;
}
.banner_two {
  background: #e6f6eb;
  margin-bottom: 3px;
}
.button_two {
  background: #e6f6eb;
  border: none;
  margin-top: 2px;
}
.donate {
  background: #008000;
  color: white;
  border: none;
  margin-top: 5px;
}
.label_two {
  background: #e6f6eb;
  color: #008000;
  border: none;
  margin-top: 2px;
}
</style>
