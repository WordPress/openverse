export const bannerNature = ["info", "success", "warning", "error"] as const
export type BannerNature = (typeof bannerNature)[number]

export const bannerVariant = ["regular", "dark"] as const
export type BannerVariant = (typeof bannerVariant)[number]
