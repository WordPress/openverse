// eslint-disable-next-line no-restricted-imports
import * as pinia from "pinia"

export const createPinia = () => pinia.createPinia()

export const setActivePinia = pinia.setActivePinia

export const PiniaVuePlugin = pinia.PiniaVuePlugin
