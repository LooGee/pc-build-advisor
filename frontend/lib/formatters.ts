export function formatPrice(price: number, currency: string = "KRW"): string {
  if (currency === "KRW") {
    return `₩${price.toLocaleString("ko-KR")}`;
  }
  return `$${price.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatBenchmark(score: number): string {
  if (score >= 1000) return `${(score / 1000).toFixed(1)}K`;
  return score.toString();
}
