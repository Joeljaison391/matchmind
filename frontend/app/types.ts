export interface TraceStep {
  agent: string;
  tool: string;
  query: string;
  duration_ms: number;
  score: number | null;
}

export interface TraceInfo {
  agents_fired: string[];
  total_ms: number;
  steps: TraceStep[];
  eval: { relevance: number; completeness: number; accuracy: number; avg: number } | null;
  retry_marker: "PASS" | "RETRY" | null;
}

export interface ResponsePayload {
  type: "match_card" | "itinerary" | "business_list" | "faq_answer" | "team_info";
  data: Record<string, unknown>;
  text: string;
}

export interface ChatApiResponse {
  response: ResponsePayload;
  trace: TraceInfo;
  session_id: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  payload?: ResponsePayload;
  trace?: TraceInfo;
}

// domain shapes
export interface MatchCard {
  match_id: string;
  home_team: string;
  away_team: string;
  kickoff_local: string;
  kickoff_utc: string;
  venue_name: string | null;
  city: string;
  group: string;
  round_type: string;
  broadcast: string[];
}

export interface ItineraryStep {
  time: string;
  activity: string;
  location: string;
  transport_mode: string;
  notes: string | null;
}

export interface Business {
  name: string;
  category: string;
  cuisine: string;
  halal_flag: boolean;
  vegan_flag: boolean;
  rating: number;
  price_range: string;
  distance_to_venue_m: number;
  address: string;
}
