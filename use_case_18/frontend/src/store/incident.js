import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export const useIncidentStore = create(
  immer((set) => ({
    draft: {}, transcript: [],
    addPatch: (patch) =>
      set((s) => { patch.forEach(({ op, path, value }) => {
        const keys = path.slice(1).split('/');
        let ref = s.draft;
        while (keys.length > 1) ref = ref[keys.shift()];
        if (op === 'add' || op === 'replace') ref[keys[0]] = value;
      }); }),
    appendChat: (msg) => set((s) => { s.transcript.push(msg); })
  }))
);
