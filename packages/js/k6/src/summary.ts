import { SummaryData, textSummary } from "./jslib-shim"

export function handleSummary(data: SummaryData) {
  console.log(textSummary(data, { enableColors: true }))

  const textSummaryOutPath = __ENV.text_summary ?? "summary.txt"
  return {
    [textSummaryOutPath]: textSummary(data, { enableColors: false }),
  }
}
