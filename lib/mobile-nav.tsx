"use client";

import { createContext, useContext, useState } from "react";

// Shared open/close state for the mobile nav drawer, so the TopBar hamburger
// and the MobileDrawer (rendered as siblings under the shell) can talk.
const MobileNavContext = createContext<{ open: boolean; setOpen: (v: boolean) => void }>({
  open: false,
  setOpen: () => {},
});

export function MobileNavProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return <MobileNavContext.Provider value={{ open, setOpen }}>{children}</MobileNavContext.Provider>;
}

export const useMobileNav = () => useContext(MobileNavContext);
