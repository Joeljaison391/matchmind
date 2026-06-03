import type { ResponsePayload, MatchCard as MatchCardData, ItineraryStep, Business } from "@/app/types";
import MatchCard from "@/components/Cards/MatchCard";
import ItineraryTimeline from "@/components/Cards/ItineraryTimeline";
import BusinessCard from "@/components/Cards/BusinessCard";
import FAQAnswer from "@/components/Cards/FAQAnswer";

export default function ResponseRenderer({ payload }: { payload: ResponsePayload }) {
  const { type, data, text } = payload;

  if (type === "match_card") {
    const matches = (data as { matches: MatchCardData[] }).matches ?? [];
    return (
      <div className="space-y-2">
        <p className="text-sm text-gray-300">{text}</p>
        {matches.map((m) => (
          <MatchCard key={m.match_id} match={m} />
        ))}
      </div>
    );
  }

  if (type === "itinerary") {
    const steps = (data as { steps: ItineraryStep[] }).steps ?? [];
    return (
      <div className="space-y-2">
        <p className="text-sm text-gray-300">{text}</p>
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
          <ItineraryTimeline steps={steps} />
        </div>
      </div>
    );
  }

  if (type === "business_list") {
    const businesses = (data as { businesses: Business[] }).businesses ?? [];
    return (
      <div className="space-y-2">
        <p className="text-sm text-gray-300">{text}</p>
        {businesses.map((b, i) => (
          <BusinessCard key={i} biz={b} />
        ))}
      </div>
    );
  }

  if (type === "faq_answer" && data && (data as { answer?: string }).answer) {
    return <FAQAnswer faq={data as { question: string; answer: string; tags?: string[] }} />;
  }

  return <p className="text-sm text-gray-300 leading-relaxed">{text}</p>;
}
