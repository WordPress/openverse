const GALLERY_SETS = ["universe", "pottery", "olympics", "random"] as const
export type GallerySet = (typeof GALLERY_SETS)[number]
