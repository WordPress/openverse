import { SET_SHOW_NOTIFICATION } from '~/constants/mutation-types'
import { NOTIFICATION_ACTION } from '~/constants/action-types'
import local from '~/utils/local'

export const state = () => ({
  // To test, set this to true
  showNotification: false,
  // i18n keys for the notification text and 'Okay' and 'Dismiss' buttons
  // if notificationDismiss is null, only a cross icon is shown
  // if notificationOkay is null, there is no action button on the notification
  notificationText: 'header.notification.text',
  notificationDismiss: null, //'header.notification.dismiss',
  notificationOkay: null, // 'header.notification.okay',
})

/* eslint no-param-reassign: ["error", { "props": false }] */
export const mutations = {
  [SET_SHOW_NOTIFICATION](_state, { showNotification }) {
    _state.showNotification = showNotification
    local.set(process.env.notificationStorageKey, showNotification)
  },
}

export const actions = {
  // Add any function that should be called when notification
  // banner 'Okay' button is clicked here
  [NOTIFICATION_ACTION]({ commit, dispatch }, params) {
    console.log(commit, dispatch, params)
  },
}
