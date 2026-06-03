import type { MatchCard as MatchCardData } from "@/app/types";
import { flag, GROUP_STYLES } from "@/lib/teams";

function kickoffLabel(local: string | null) {
  if (!local) return "Kickoff TBD";
  const d = new Date(local);
  const now = new Date();
  const diffH = (d.getTime() - now.getTime()) / 3_600_000;

  const time = d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const date = d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

  if (diffH < 0) return `${date} · ${time}`;
  if (diffH < 3) return `🔴 LIVE / starting soon`;
  if (diffH < 24) return `Today · ${time}`;
  if (diffH < 48) return `Tomorrow · ${time}`;
  return `${date} · ${time}`;
}

export default function MatchCard({ match }: { match: MatchCardData }) {
  const groupStyle = match.group ? GROUP_STYLES[match.group] ?? "" : "";

  return (
    <div className="bg-[#111218] border border-gray-800 rounded-2xl overflow-hidden pitch-glow">
      {/* top bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800/60 bg-black/20">
        <div className="flex items-center gap-2">
          {match.group && (
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${groupStyle}`}>
              Group {match.group}
            </span>
          )}
          <span className="text-xs text-gray-500 capitalize">
            {match.round_type?.replace(/_/g, " ")}
          </span>
        </div>
        {match.broadcast?.length > 0 && (
          <span className="text-xs text-gray-600">{match.broadcast.slice(0, 2).join(" · ")}</span>
        )}
      </div>

      {/* teams */}
      <div className="px-4 py-4 flex items-center gap-3">
        {/* home */}
        <div className="flex-1 flex flex-col items-end gap-1">
          <span className="text-2xl">{flag(match.home_team)}</span>
          <span className="text-sm font-bold text-white text-right">{match.home_team}</span>
        </div>

        {/* vs divider */}
        <div className="flex flex-col items-center gap-1 px-2">
          <span className="text-xs font-mono text-gray-600 bg-gray-900 px-2 py-1 rounded-lg border border-gray-800">
            VS
          </span>
        </div>

        {/* away */}
        <div className="flex-1 flex flex-col items-start gap-1">
          <span className="text-2xl">{flag(match.away_team)}</span>
          <span className="text-sm font-bold text-white">{match.away_team}</span>
        </div>
      </div>

      {/* venue + kickoff */}
      <div className="px-4 pb-3 space-y-1.5">
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <span className="text-amber-500">🏟</span>
          <span className="text-amber-400/80 font-medium">{match.venue_name ?? "Venue TBD"}</span>
          {match.city && <span className="text-gray-600">· {match.city}</span>}
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <span>🕐</span>
          <span className="text-gray-300 font-medium">{kickoffLabel(match.kickoff_local)}</span>
        </div>
      </div>
    </div>
  );
}
