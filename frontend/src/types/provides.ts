import type { InjectionKey, Ref } from "vue"

export const IsHeaderScrolledKey =
  process.env.NODE_ENV === "test"
    ? "IsHeaderScrolledKey"
    : (Symbol() as InjectionKey<Ref<boolean>>)
export const IsSidebarVisibleKey =
  process.env.NODE_ENV === "test"
    ? "IsHeaderScrolledKey"
    : (Symbol() as InjectionKey<Ref<boolean>>)
