import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"
import { AudioDetail, ImageDetail } from "~/types/media"

export type ResultKind = "search" | "related" | "collection"
export type ImageResults = {
  type: typeof IMAGE
  items: ImageDetail[]
}
export type AudioResults = {
  type: typeof AUDIO
  items: AudioDetail[]
}
export type AllMediaResults = {
  type: typeof ALL_MEDIA
  items: (AudioDetail | ImageDetail)[]
}
export type Results = AudioResults | ImageResults | AllMediaResults
