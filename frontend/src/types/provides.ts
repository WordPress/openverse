import type { InjectionKey, Ref } from "@nuxtjs/composition-api"

export const IsHeaderScrolledKey = Symbol() as InjectionKey<Ref<boolean>>
export const IsSidebarVisibleKey = Symbol() as InjectionKey<Ref<boolean>>
