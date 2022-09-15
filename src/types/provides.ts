import type { InjectionKey, Ref } from '@nuxtjs/composition-api'

export const IsMinScreenMdKey = Symbol() as InjectionKey<Ref<boolean>>
export const IsMinScreenLgKey = Symbol() as InjectionKey<Ref<boolean>>
export const IsHeaderScrolledKey = Symbol() as InjectionKey<Ref<boolean>>
