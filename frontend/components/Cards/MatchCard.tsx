import type { MatchCard as MatchCardData } from "@/app/types";

export default function MatchCard({ match }: { match: MatchCardData }) {
  const kickoff = match.kickoff_local
    ? new Date(match.kickoff_local).toLocaleString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "TBD";

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-green-400 font-medium uppercase tracking-wide">
          {match.round_type} {match.group ? `· Group ${match.group}` : ""}
        </span>
        {match.broadcast?.length > 0 && (
          <span className="text-xs text-gray-500">{match.broadcast.join(", ")}</span>
        )}
      </div>

      <div className="flex items-center justify-between gap-4 py-2">
        <span className="text-lg font-bold text-white flex-1 text-right">{match.home_team}</span>
        <span className="text-gray-500 text-sm font-mono">vs</span>
        <span className="text-lg font-bold text-white flex-1">{match.away_team}</span>
      </div>

      <div className="text-sm text-gray-400 space-y-1">
        <div>🏟 {match.venue_name ?? "Venue TBD"}, {match.city}</div>
        <div>🕐 {kickoff}</div>
      </div>
    </div>
  );
}
