export interface Budget {
  min: number | null;
  max: number;
  currency: string;
}

export interface Preferences {
  color: string | null;
  size: string | null;
  brands: string[];
  features: string[];
  monitor_resolution: string | null;
  target_fps: number | null;
}

export interface AnalyzedRequirements {
  primary_use: string;
  specific_software_games: string[];
  performance_tier: "min" | "mid" | "max";
  budget: Budget;
  preferences: Preferences;
  priority: string;
  additional_notes: string;
}

export interface PriceSource {
  source: string;
  price_krw: number;
  url: string;
  in_stock: boolean;
  shipping?: string;
}

export interface ComponentPriceInfo {
  price_krw: number;
  sources: PriceSource[];
}

export interface QuoteComponent {
  category: string;
  id: string;
  brand: string;
  model: string;
  image_url: string | null;
  specifications: Record<string, any>;
  price_info: ComponentPriceInfo;
  compatibility_status: "ok" | "warning" | "error";
  compatibility_notes: string;
}

export interface CompatibilityIssue {
  issue_id: string;
  severity: "error" | "warning" | "info" | "suggestion";
  title_ko: string;
  message_ko: string;
  solution_ko: string;
  icon: string;
}

export interface EstimatedPerformance {
  cpu_benchmark_score: number | null;
  gpu_benchmark_score: number | null;
  estimated_gaming_fps_1080p: number | null;
  estimated_gaming_fps_1440p: number | null;
  estimated_power_consumption_w: number | null;
}

export interface QuoteTier {
  tier: "minimum" | "balanced" | "maximum";
  tier_name: string;
  tier_description: string;
  total_price_krw: number;
  components_price_krw: number;
  shipping_cost_krw: number;
  components: QuoteComponent[];
  compatibility: {
    is_compatible: boolean;
    issues: CompatibilityIssue[];
  };
  estimated_performance: EstimatedPerformance | null;
}

export interface QuoteResponse {
  id: string;
  user_input: string;
  analyzed_requirements: AnalyzedRequirements;
  quotes: QuoteTier[];
  created_at: string;
  expires_at: string | null;
}
