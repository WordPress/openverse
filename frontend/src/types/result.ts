import { AUDIO, IMAGE } from "~/constants/media"
import { AudioDetail, ImageDetail } from "~/types/media"

export type ResultKind = "search" | "related" | "collection"
export type Results =
  | {
      type: typeof AUDIO
      items: AudioDetail[]
    }
  | {
      type: typeof IMAGE
      items: ImageDetail[]
    }
