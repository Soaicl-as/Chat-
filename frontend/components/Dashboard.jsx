
import React, { useState } from 'react';
import axios from 'axios';
import LogViewer from './LogViewer';

export default function Dashboard({ sessionId }) {
  const [target, setTarget] = useState('');
  const [listType, setListType] = useState('followers');
  const [message, setMessage] = useState('');
  const [count, setCount] = useState(10);
  const [minDelay, setMinDelay] = useState(5);
  const [maxDelay, setMaxDelay] = useState(10);
  const [showLogs, setShowLogs] = useState(false);

  const startBot = async () => {
    try {
      await axios.post('/api/send_dms', {
        session_id: sessionId,
        target_username: target,
        list_type: listType,
        message,
        count,
        min_delay: minDelay,
        max_delay: maxDelay
      });
      setShowLogs(true);
    } catch (err) {
      alert('Error starting bot: ' + err.response.data.detail);
    }
  };

  return (
    <div className="space-y-4">
      <input className="border p-2 w-full" placeholder="Target username" value={target} onChange={e => setTarget(e.target.value)} />
      <select className="border p-2 w-full" value={listType} onChange={e => setListType(e.target.value)}>
        <option value="followers">Followers</option>
        <option value="following">Following</option>
      </select>
      <textarea className="border p-2 w-full" placeholder="Message" rows={3} value={message} onChange={e => setMessage(e.target.value)} />
      <input className="border p-2 w-full" type="number" placeholder="Number of recipients" value={count} onChange={e => setCount(Number(e.target.value))} />
      <div className="flex space-x-2">
        <input className="border p-2 w-full" type="number" placeholder="Min delay (sec)" value={minDelay} onChange={e => setMinDelay(Number(e.target.value))} />
        <input className="border p-2 w-full" type="number" placeholder="Max delay (sec)" value={maxDelay} onChange={e => setMaxDelay(Number(e.target.value))} />
      </div>
      <button onClick={startBot} className="bg-green-600 text-white px-4 py-2 rounded">Start Bot</button>
      {showLogs && <LogViewer sessionId={sessionId} />}
    </div>
  );
}
