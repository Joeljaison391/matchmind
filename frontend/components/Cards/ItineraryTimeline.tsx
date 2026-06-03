import type { ItineraryStep } from "@/app/types";

const TRANSPORT_ICON: Record<string, string> = {
  shuttle: "🚌",
  walk: "🚶",
  rideshare: "🚗",
  metro: "🚇",
  taxi: "🚕",
  bus: "🚍",
  train: "🚆",
};

export default function ItineraryTimeline({ steps }: { steps: ItineraryStep[] }) {
  return (
    <div className="space-y-0">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className="w-8 h-8 rounded-full bg-green-500/20 border border-green-500/40 flex items-center justify-center text-xs font-bold text-green-400">
              {step.time}
            </div>
            {i < steps.length - 1 && (
              <div className="w-px flex-1 bg-gray-700 my-1" />
            )}
          </div>
          <div className="pb-4 flex-1">
            <div className="flex items-start gap-2">
              <span className="text-base">
                {TRANSPORT_ICON[step.transport_mode?.toLowerCase()] ?? "📍"}
              </span>
              <div>
                <p className="text-sm font-medium text-white">{step.activity}</p>
                <p className="text-xs text-gray-500">{step.location}</p>
                {step.notes && (
                  <p className="text-xs text-gray-600 mt-0.5 italic">{step.notes}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
