"use client";

import { CacheProvider } from "@chakra-ui/next-js";
import { ChakraProvider } from "@chakra-ui/react";
import { AnimatePresence } from "framer-motion";
import { ReactNode } from "react";
import { theme } from "@/theme";

type ProvidersProps = {
  children: ReactNode;
};

export function Providers({ children }: ProvidersProps) {
  return (
    <CacheProvider>
      <ChakraProvider theme={theme} cssVarsRoot=":root">
        <AnimatePresence mode="wait">{children}</AnimatePresence>
      </ChakraProvider>
    </CacheProvider>
  );
}
