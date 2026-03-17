export const COMPONENT_CATEGORIES = [
  { key: "cpu", label: "CPU" },
  { key: "gpu", label: "그래픽카드" },
  { key: "motherboard", label: "메인보드" },
  { key: "ram", label: "RAM" },
  { key: "storage", label: "저장장치" },
  { key: "psu", label: "파워서플라이" },
  { key: "case", label: "케이스" },
  { key: "cooler", label: "CPU 쿨러" },
] as const;

export const PRICE_SOURCES = {
  danawa: { label: "다나와", color: "#3b82f6" },
  compuzone: { label: "컴퓨존", color: "#10b981" },
  coupang: { label: "쿠팡", color: "#f97316" },
  pcpartpicker: { label: "PCPartPicker", color: "#8b5cf6" },
} as const;

export const TIER_LABELS = {
  minimum: "최소 요구사항",
  balanced: "균형 조화형",
  maximum: "최고 성능형",
} as const;
