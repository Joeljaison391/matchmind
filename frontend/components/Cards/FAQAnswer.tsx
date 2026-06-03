interface FAQData {
  question: string;
  answer: string;
  tags?: string[];
  score?: number;
}

export default function FAQAnswer({ faq }: { faq: FAQData }) {
  return (
    <div className="bg-[#111218] border border-gray-800 rounded-2xl overflow-hidden pitch-glow">
      <div className="px-4 py-2 border-b border-gray-800/60 bg-black/20">
        <span className="text-xs font-bold text-green-500 uppercase tracking-widest">
          ⚽ World Cup FAQ
        </span>
      </div>
      <div className="px-4 py-3 space-y-3">
        <p className="text-xs text-gray-500 italic leading-relaxed">&ldquo;{faq.question}&rdquo;</p>
        <p className="text-sm text-gray-100 leading-relaxed">{faq.answer}</p>
        {faq.tags && faq.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {faq.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs bg-gray-900 text-gray-500 border border-gray-800 px-2 py-0.5 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
