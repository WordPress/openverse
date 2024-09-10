export const bannerNature = ["info", "success", "warning", "error"] as const
export type BannerNature = (typeof bannerNature)[number]
