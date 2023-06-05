import type { InjectionKey, Ref } from "vue"

export const IsHeaderScrolledKey = Symbol() as InjectionKey<Ref<boolean>>
export const IsSidebarVisibleKey = Symbol() as InjectionKey<Ref<boolean>>
export const ShowScrollButtonKey = Symbol() as InjectionKey<Ref<boolean>>
