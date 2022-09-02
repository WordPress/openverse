import { defineStore } from 'pinia'

export type SnackbarState = 'not_shown' | 'visible' | 'dismissed'

export interface UiState {
  /**
   * whether to show the instructions snackbar.
   */
  instructionsSnackbarState: SnackbarState
}

export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    instructionsSnackbarState: 'not_shown',
  }),

  getters: {
    areInstructionsVisible(state) {
      return state.instructionsSnackbarState === 'visible'
    },
  },

  actions: {
    showInstructionsSnackbar() {
      if (this.instructionsSnackbarState === 'not_shown') {
        this.instructionsSnackbarState = 'visible'
      }
    },
    hideInstructionsSnackbar() {
      this.instructionsSnackbarState = 'dismissed'
    },
  },
})
