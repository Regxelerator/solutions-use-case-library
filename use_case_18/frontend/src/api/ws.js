import { useIncidentStore } from '../store/incident';

let socket;

export const connectAgent = () => {
  if (socket?.readyState === 1) return socket;

  socket = new WebSocket('ws://localhost:8000/agent/run');
  socket.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'chat')        useIncidentStore.getState().appendChat(msg.payload);
    if (msg.type === 'json_patch')  useIncidentStore.getState().addPatch(msg.payload);
  };
  return socket;
};

export const sendUserMsg = (text) =>
  socket?.readyState === 1 && socket.send(JSON.stringify({ role: 'user', content: text }));
