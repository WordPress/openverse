<template>
  <div class="notification__wrapper">
    <p class="notification__text">
      {{ $t(text) }}
    </p>
    <div class="notification__actions">
      <button
        v-if="!!okayLabel"
        class="button is-success small"
        @click="handleOkayClick"
      >
        {{ $t(okayLabel) }}
      </button>
      <button
        class="button is-text small dismiss-button"
        @click="handleDismissClick"
      >
        <span v-if="!!dismissLabel">{{ $t(dismissLabel) }}</span>
        <svg
          v-else
          viewBox="0 0 30 30"
          width="15"
          height="15"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18.9094 15L24.7729 9.13652C25.4924 8.41699 25.4924 7.25039 24.7729 6.53027L23.4697 5.22715C22.7502 4.50762 21.5836 4.50762 20.8635 5.22715L15 11.0906L9.13652 5.22715C8.41699 4.50762 7.25039 4.50762 6.53027 5.22715L5.22715 6.53027C4.50762 7.2498 4.50762 8.41641 5.22715 9.13652L11.0906 15L5.22715 20.8635C4.50762 21.583 4.50762 22.7496 5.22715 23.4697L6.53027 24.7729C7.2498 25.4924 8.41699 25.4924 9.13652 24.7729L15 18.9094L20.8635 24.7729C21.583 25.4924 22.7502 25.4924 23.4697 24.7729L24.7729 23.4697C25.4924 22.7502 25.4924 21.5836 24.7729 20.8635L18.9094 15Z"
            fill="currentColor"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { SET_SHOW_NOTIFICATION } from '~/constants/mutation-types'
import { NOTIFICATION } from '~/constants/store-modules'
import { NOTIFICATION_ACTION } from '~/constants/action-types'

export default {
  name: 'NotificationBanner',
  computed: {
    ...mapState({
      text: (state) => state.notification.notificationText,
      dismissLabel: (state) => state.notification.notificationDismiss,
      okayLabel: (state) => state.notification.notificationOkay,
    }),
  },
  methods: {
    handleDismissClick() {
      this.$store.commit(`${NOTIFICATION}/${SET_SHOW_NOTIFICATION}`, {
        showNotification: false,
      })
    },
    handleOkayClick() {
      this.$store.dispatch(`${NOTIFICATION}/${NOTIFICATION_ACTION}`)
    },
  },
}
</script>

<style scoped lang="scss">
$bgColor: #e6f6eb;
.notification {
  &__wrapper {
    background-color: $bgColor;
    padding: 0.5rem 2rem;
    @include tablet {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  &__text {
    @include mobile {
      text-align: center;
    }
  }
  &__actions {
    display: flex;
    // double selector to increase specificity (to override other issues)
    .dismiss-button {
      color: $color-dark-success;
      padding: $space-small calc(#{$space-normal} + 0.2rem) !important;
      white-space: nowrap;
    }
    @include mobile {
      margin-top: $space-small;
      justify-content: center;
    }

    @include tablet {
      padding-left: $space-normal;
    }
  }
}

.button {
  text-transform: none;
  font-family: inherit;
}
</style>
