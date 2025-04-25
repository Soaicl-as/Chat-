
import React, { useEffect, useState } from 'react';

export default function LogViewer({ sessionId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const evtSource = new EventSource(`/api/logs/${sessionId}`);
    evtSource.onmessage = (e) => {
      setLogs(prev => [...prev, e.data]);
    };
    return () => evtSource.close();
  }, [sessionId]);

  return (
    <div className="border p-2 bg-black text-white h-64 overflow-y-scroll mt-4">
      {logs.map((log, idx) => (
        <div key={idx} className="whitespace-pre-wrap">{log}</div>
      ))}
    </div>
  );
}
