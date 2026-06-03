export const TEAM_FLAGS: Record<string, string> = {
  Brazil: "🇧🇷", Argentina: "🇦🇷", France: "🇫🇷", Germany: "🇩🇪",
  Spain: "🇪🇸", England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", Portugal: "🇵🇹", Netherlands: "🇳🇱",
  Belgium: "🇧🇪", Italy: "🇮🇹", Mexico: "🇲🇽", "United States": "🇺🇸",
  USA: "🇺🇸", Canada: "🇨🇦", Japan: "🇯🇵", "South Korea": "🇰🇷",
  Morocco: "🇲🇦", Senegal: "🇸🇳", Australia: "🇦🇺", "Saudi Arabia": "🇸🇦",
  Iran: "🇮🇷", Uruguay: "🇺🇾", Colombia: "🇨🇴", Ecuador: "🇪🇨",
  Chile: "🇨🇱", Poland: "🇵🇱", Switzerland: "🇨🇭", Croatia: "🇭🇷",
  Serbia: "🇷🇸", Denmark: "🇩🇰", Austria: "🇦🇹", Ukraine: "🇺🇦",
  Tunisia: "🇹🇳", Cameroon: "🇨🇲", Ghana: "🇬🇭", Nigeria: "🇳🇬",
  Egypt: "🇪🇬", Algeria: "🇩🇿", "Costa Rica": "🇨🇷", Panama: "🇵🇦",
  Honduras: "🇭🇳", Jamaica: "🇯🇲", "New Zealand": "🇳🇿", Indonesia: "🇮🇩",
  Venezuela: "🇻🇪", Paraguay: "🇵🇾", Peru: "🇵🇪", Wales: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
  Scotland: "🏴󠁧󠁢󠁳󠁣󠁴󠁿", Turkey: "🇹🇷", Greece: "🇬🇷", Romania: "🇷🇴",
  Hungary: "🇭🇺", "Czech Republic": "🇨🇿", Slovakia: "🇸🇰", Guatemala: "🇬🇹",
  "Ivory Coast": "🇨🇮", Mali: "🇲🇱", Zambia: "🇿🇲", Sudan: "🇸🇩",
};

export const GROUP_STYLES: Record<string, string> = {
  A: "bg-red-950 text-red-400 border border-red-800/50",
  B: "bg-blue-950 text-blue-400 border border-blue-800/50",
  C: "bg-emerald-950 text-emerald-400 border border-emerald-800/50",
  D: "bg-amber-950 text-amber-400 border border-amber-800/50",
  E: "bg-purple-950 text-purple-400 border border-purple-800/50",
  F: "bg-orange-950 text-orange-400 border border-orange-800/50",
  G: "bg-pink-950 text-pink-400 border border-pink-800/50",
  H: "bg-teal-950 text-teal-400 border border-teal-800/50",
};

export function flag(team: string) {
  return TEAM_FLAGS[team] ?? "🏳";
}

export function walkMinutes(metres: number) {
  return Math.max(1, Math.ceil(metres / 80));
}
