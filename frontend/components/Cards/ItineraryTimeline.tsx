import type { ItineraryStep } from "@/app/types";

const TRANSPORT: Record<string, { icon: string; color: string }> = {
  shuttle: { icon: "🚌", color: "bg-blue-950 text-blue-400 border-blue-900/50" },
  walk:    { icon: "🚶", color: "bg-gray-900 text-gray-400 border-gray-800" },
  rideshare: { icon: "🚗", color: "bg-purple-950 text-purple-400 border-purple-900/50" },
  metro:   { icon: "🚇", color: "bg-orange-950 text-orange-400 border-orange-900/50" },
  taxi:    { icon: "🚕", color: "bg-yellow-950 text-yellow-400 border-yellow-900/50" },
  bus:     { icon: "🚍", color: "bg-teal-950 text-teal-400 border-teal-900/50" },
  train:   { icon: "🚆", color: "bg-indigo-950 text-indigo-400 border-indigo-900/50" },
};

function getTransport(mode: string) {
  return TRANSPORT[mode?.toLowerCase()] ?? { icon: "📍", color: "bg-gray-900 text-gray-500 border-gray-800" };
}

export default function ItineraryTimeline({ steps }: { steps: ItineraryStep[] }) {
  return (
    <div>
      {steps.map((step, i) => {
        const t = getTransport(step.transport_mode);
        const isLast = i === steps.length - 1;
        return (
          <div key={i} className="flex gap-3">
            {/* left rail */}
            <div className="flex flex-col items-center">
              <div className="w-10 shrink-0 h-10 rounded-full bg-green-950 border border-green-800/60 flex flex-col items-center justify-center">
                <span className="text-green-400 font-bold text-[10px] leading-none">{step.time}</span>
              </div>
              {!isLast && <div className="w-px flex-1 bg-gradient-to-b from-green-800/40 to-gray-800/40 my-1" />}
            </div>

            {/* content */}
            <div className={`flex-1 ${isLast ? "pb-0" : "pb-4"}`}>
              <div className="flex items-start gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full border font-medium shrink-0 mt-0.5 ${t.color}`}>
                  {t.icon} {step.transport_mode}
                </span>
              </div>
              <p className="text-sm font-semibold text-white mt-1.5">{step.activity}</p>
              <p className="text-xs text-gray-500 mt-0.5">{step.location}</p>
              {step.notes && (
                <p className="text-xs text-gray-600 mt-1 italic leading-relaxed">{step.notes}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
