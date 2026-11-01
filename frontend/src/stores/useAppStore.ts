
import { create } from "zustand";

export interface EvidenceRegion {
  page_number: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface CitationTarget {
  documentId: string;
  evidenceId: string;
  regions: EvidenceRegion[];
}

interface AppState {
  sidebarExpanded: boolean;
  activeConversationId: string | null;
  activeDocumentId: string | null;
  citationTarget: CitationTarget | null;

  toggleSidebar: () => void;
  setSidebarExpanded: (expanded: boolean) => void;
  setActiveConversation: (id: string | null) => void;
  setActiveDocument: (id: string | null) => void;
  setCitationTarget: (target: CitationTarget | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarExpanded: true,
  activeConversationId: null,
  activeDocumentId: null,
  citationTarget: null,

  toggleSidebar: () =>
    set((state) => ({
      sidebarExpanded: !state.sidebarExpanded,
    })),

  setSidebarExpanded: (expanded) =>
    set({ sidebarExpanded: expanded }),

  setActiveConversation: (id) =>
    set({ activeConversationId: id }),

  setActiveDocument: (id) =>
    set({ activeDocumentId: id }),

  setCitationTarget: (target) =>
    set({ citationTarget: target }),
}));
