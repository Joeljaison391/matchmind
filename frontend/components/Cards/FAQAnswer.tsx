interface FAQData {
  question: string;
  answer: string;
  tags?: string[];
  score?: number;
}

export default function FAQAnswer({ faq }: { faq: FAQData }) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-2">
      <p className="text-xs text-green-400 font-medium uppercase tracking-wide">FAQ</p>
      <p className="text-sm text-gray-300 italic">{faq.question}</p>
      <p className="text-sm text-white leading-relaxed">{faq.answer}</p>
      {faq.tags && faq.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 pt-1">
          {faq.tags.map((tag) => (
            <span key={tag} className="text-xs bg-gray-800 text-gray-500 px-2 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
