<template>
  <section class="section">
    <div
      class="padding-small"
      style="background: #e6f6eb;"
      v-bind:class="{ change: task.id }"
    >
      <div class="columns">
        <div class="column is-8">
          <p class="margin-top-normal">
            If you donate $5 today, and everyone else does the same, we can keep
            growing our database of freely reusable content. For you. For all of
            us.
          </p>
        </div>

        <div class="column">
          <button
            type="submit"
            class="button is-success is-small position"
            v-on:click="redirect"
          >
            <i
              class="icon cc-letterheart-filled margin-right-small is-size-5 padding-top-smaller"
            />Yes, I’ll donate now
          </button>
        </div>

        <div class="column">
          <button
            class="button is-small position"
            style="border: none; background: #e6f6eb; color: #008000;"
            v-on:click="onclick"
          >
            Not today
          </button>
        </div>
        <div class="column">
          <button class="button is-text button_two" v-on:click="onclick">
            x
          </button>
        </div>
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
@media only screen and (max-width: 767px) {
  .button_two {
    display: none;
  }
}
@media only screen and (max-width: 767px) {
  .position {
    width: 100%;
  }
}
</style>
