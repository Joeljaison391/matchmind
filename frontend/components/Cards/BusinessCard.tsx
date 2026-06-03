import type { Business } from "@/app/types";
import { walkMinutes } from "@/lib/teams";

const CATEGORY_ICONS: Record<string, string> = {
  restaurant: "🍽", cafe: "☕", bar: "🍺", "fast food": "🍔",
  pizza: "🍕", bakery: "🥐", dessert: "🍦", food: "🍽",
  pub: "🍻", rooftop: "🌆", brewery: "🍺",
};

function categoryIcon(cat: string) {
  return CATEGORY_ICONS[cat?.toLowerCase()] ?? "🍽";
}

function Stars({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  return (
    <span className="flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={`text-xs ${
            i < full ? "text-amber-400" : i === full && half ? "text-amber-400/50" : "text-gray-700"
          }`}
        >
          ★
        </span>
      ))}
      <span className="text-xs text-gray-500 ml-1">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function BusinessCard({ biz }: { biz: Business }) {
  const mins = walkMinutes(biz.distance_to_venue_m);

  return (
    <div className="bg-[#111218] border border-gray-800 rounded-xl p-3 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-base shrink-0">{categoryIcon(biz.category)}</span>
          <span className="font-semibold text-white text-sm truncate">{biz.name}</span>
        </div>
        <span className="text-xs text-gray-500 shrink-0 font-mono">{biz.price_range}</span>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap mb-2">
        <span className="text-xs text-gray-500 capitalize">{biz.category}</span>
        {biz.cuisine && <span className="text-xs text-gray-600">· {biz.cuisine}</span>}
        {biz.halal_flag && (
          <span className="text-xs bg-green-950 text-green-400 border border-green-900/60 px-1.5 py-0.5 rounded-full font-medium">
            ✓ Halal
          </span>
        )}
        {biz.vegan_flag && (
          <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-900/60 px-1.5 py-0.5 rounded-full font-medium">
            🌱 Vegan
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <Stars rating={biz.rating} />
        <span className="text-xs text-gray-500 flex items-center gap-1">
          🚶 {mins} min walk
        </span>
      </div>

      {biz.address && (
        <p className="text-xs text-gray-700 truncate mt-1.5">{biz.address}</p>
      )}
    </div>
  );
}
