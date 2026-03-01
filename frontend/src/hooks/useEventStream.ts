import { useEffect, useState, useRef, useCallback } from "react";

interface StreamEvent {
  type: string;
  message?: string;
  success?: boolean;
  timestamp: string;
}

export function useEventStream(sessionId: string | null) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!sessionId || eventSourceRef.current) return;

    const eventSource = new EventSource(`http://localhost:8001/events/stream?session_id=${sessionId}`);
    eventSourceRef.current = eventSource;

    eventSource.addEventListener("connected", (event) => {
      setIsConnected(true);
      const data = JSON.parse(event.data);
      console.log("EventStream connected:", data);
    });

    eventSource.addEventListener("event", (event) => {
      const data: StreamEvent = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    });

    eventSource.onerror = (error) => {
      console.error("EventStream error:", error);
      setIsConnected(false);
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [sessionId]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  useEffect(() => {
    if (sessionId) {
      connect();
    }
    return () => disconnect();
  }, [sessionId, connect, disconnect]);

  return {
    events,
    isConnected,
    clearEvents,
  };
}
