// Courtesy of @mbforbes via https://gist.github.com/robingustafsson/7dd6463d85efdddbb0e4bcd3ecc706e1?permalink_comment_id=4884925#gistcomment-4884925

import { createHMAC } from "k6/crypto"

import type { Algorithm } from "k6/crypto"

export function sign(
  data: string | ArrayBuffer,
  hashAlg: Algorithm,
  secret: string | ArrayBuffer
) {
  const hasher = createHMAC(hashAlg, secret)
  hasher.update(data)
  return hasher.digest("base64rawurl")
}
