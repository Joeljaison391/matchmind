import type { Business } from "@/app/types";

function Stars({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  return (
    <span className="text-yellow-400 text-xs">
      {"★".repeat(full)}{"☆".repeat(5 - full)}
      <span className="text-gray-500 ml-1">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function BusinessCard({ biz }: { biz: Business }) {
  const dist =
    biz.distance_to_venue_m < 1000
      ? `${biz.distance_to_venue_m}m`
      : `${(biz.distance_to_venue_m / 1000).toFixed(1)}km`;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-3 space-y-1">
      <div className="flex items-start justify-between gap-2">
        <span className="font-semibold text-white text-sm">{biz.name}</span>
        <span className="text-xs text-gray-500 shrink-0">{biz.price_range}</span>
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-gray-400">{biz.category}</span>
        {biz.cuisine && <span className="text-xs text-gray-500">· {biz.cuisine}</span>}
        {biz.halal_flag && (
          <span className="text-xs bg-green-900/50 text-green-400 px-1.5 py-0.5 rounded">halal</span>
        )}
        {biz.vegan_flag && (
          <span className="text-xs bg-emerald-900/50 text-emerald-400 px-1.5 py-0.5 rounded">vegan</span>
        )}
      </div>
      <div className="flex items-center justify-between">
        <Stars rating={biz.rating} />
        <span className="text-xs text-gray-500">{dist} from venue</span>
      </div>
      {biz.address && (
        <p className="text-xs text-gray-600 truncate">{biz.address}</p>
      )}
    </div>
  );
}
