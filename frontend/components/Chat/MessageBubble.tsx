import type { Message } from "@/app/types";
import ResponseRenderer from "./ResponseRenderer";
import TracePanel from "@/components/TracePanel/TracePanel";

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-green-600 text-white rounded-2xl rounded-br-sm px-4 py-2 text-sm">
          {message.text}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="max-w-[90%]">
        {message.payload ? (
          <ResponseRenderer payload={message.payload} />
        ) : (
          <p className="text-sm text-gray-300">{message.text}</p>
        )}
      </div>
      {message.trace && <TracePanel trace={message.trace} />}
    </div>
  );
}
