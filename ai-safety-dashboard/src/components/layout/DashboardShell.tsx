"use client";

import {
  Box,
  chakra,
  Divider,
  Drawer,
  DrawerContent,
  Flex,
  HStack,
  IconButton,
  Stack,
  Text,
  useDisclosure,
  VStack,
  shouldForwardProp,
  Button,
  Tag,
} from "@chakra-ui/react";
import { HamburgerIcon } from "@chakra-ui/icons";
import { motion, Variants } from "framer-motion";
import NextLink from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useMemo } from "react";

const MotionBox = chakra(motion.div, {
  shouldForwardProp: (prop) =>
    shouldForwardProp(prop) || prop === "transition" || prop === "initial",
});

type NavigationItem = {
  label: string;
  description: string;
  href: string;
  badge?: string;
};

const navigation: NavigationItem[] = [
  {
    label: "Playground",
    description: "Prompt, toggle guards, and inspect flagged spans.",
    href: "/playground",
  },
  {
    label: "Benchmark Runner",
    description: "Batch test models with live telemetry.",
    href: "/benchmark-runner",
  },
  {
    label: "Threshold Tuner",
    description: "Balance precision/recall with live charts.",
    href: "/threshold-tuner",
  },
  {
    label: "Observability",
    description: "Trend guardrail health across time slices.",
    href: "/observability",
  },
  {
    label: "Policy Editor",
    description: "Version guardrail policies with YAML validation.",
    href: "/policy-editor",
    badge: "New",
  },
];

const fadeInCard: Variants = {
  hidden: { opacity: 0, y: 6 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.24 } },
};

type DashboardShellProps = {
  children: ReactNode;
  title?: string;
  description?: string;
};

export function DashboardShell({
  children,
  title,
  description,
}: DashboardShellProps) {
  const disclosure = useDisclosure();
  const pathname = usePathname();

  const activeItem = useMemo(
    () => navigation.find((item) => pathname?.startsWith(item.href)),
    [pathname],
  );

  const sidebar = (
    <Flex
      direction="column"
      h="full"
      px={6}
      py={8}
      gap={6}
      bg="surface.base"
      borderRight="1px solid"
      borderColor="rgba(15, 23, 42, 0.08)"
    >
      <VStack align="start" spacing={1}>
        <Text fontSize="lg" fontWeight="semibold" color="accent.base">
          Aurora Labs
        </Text>
        <Text fontFamily="var(--font-dm-serif)" fontSize="2xl">
          AI Safety Guardrails
        </Text>
      </VStack>
      <Divider borderColor="rgba(15, 23, 42, 0.06)" />
      <Stack spacing={2}>
        {navigation.map((item) => {
          const isActive = pathname === item.href || activeItem === item;
          return (
            <MotionBox
              key={item.href}
              variants={fadeInCard}
              initial="hidden"
              animate="visible"
            >
              <Flex
                as={NextLink}
                href={item.href}
                direction="column"
                px={4}
                py={3}
                rounded="lg"
                transition="all 0.2s ease"
                bg={isActive ? "accent.subtle" : "transparent"}
                border="1px solid"
                borderColor={isActive ? "brand.100" : "transparent"}
                _hover={{
                  bg: "accent.subtle",
                  borderColor: "brand.100",
                  transform: "translateY(-1px)",
                }}
                onClick={disclosure.onClose}
              >
                <HStack justify="space-between" align="center">
                  <Text
                    fontWeight="semibold"
                    color={isActive ? "accent.base" : "neutral.700"}
                  >
                    {item.label}
                  </Text>
                  {item.badge && (
                    <Tag
                      size="sm"
                      borderRadius="full"
                      colorScheme="brand"
                      variant="subtle"
                    >
                      {item.badge}
                    </Tag>
                  )}
                </HStack>
                <Text fontSize="sm" color="text.muted">
                  {item.description}
                </Text>
              </Flex>
            </MotionBox>
          );
        })}
      </Stack>
      <Box mt="auto" p={4} rounded="lg" bg="surface.card" shadow="xs">
        <Text fontWeight="medium">Release channel</Text>
        <Text fontSize="sm" color="text.muted">
          Guardrail SDK v2.8.1 &nbsp;•&nbsp; Updated 2 hours ago
        </Text>
        <Button mt={4} size="sm" variant="outline">
          View changelog
        </Button>
      </Box>
    </Flex>
  );

  return (
    <Flex minH="100vh" bg="surface.subtle">
      <Box display={{ base: "none", lg: "block" }} w="320px">
        {sidebar}
      </Box>

      <Drawer
        isOpen={disclosure.isOpen}
        onClose={disclosure.onClose}
        placement="left"
        size="xs"
      >
        <DrawerContent>{sidebar}</DrawerContent>
      </Drawer>

      <Flex direction="column" flex="1" minW={0}>
        <TopBar onMenuClick={disclosure.onOpen} activeLabel={activeItem?.label}>
          {activeItem?.description ?? "Operational visibility across guardrails"}
        </TopBar>
        <MotionBox
          as="main"
          flex="1"
          px={{ base: 4, md: 8, xl: 12 }}
          py={{ base: 6, md: 10 }}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.28, ease: "easeOut" }}
        >
          {title && (
            <VStack align="start" spacing={1} mb={8}>
              <Text fontSize="sm" textTransform="uppercase" color="text.muted">
                {activeItem?.label}
              </Text>
              <Text fontFamily="var(--font-dm-serif)" fontSize="3xl">
                {title}
              </Text>
              {description && (
                <Text color="text.muted" maxW="3xl">
                  {description}
                </Text>
              )}
            </VStack>
          )}
          {children}
        </MotionBox>
      </Flex>
    </Flex>
  );
}

type TopBarProps = {
  onMenuClick: () => void;
  children: ReactNode;
  activeLabel?: string;
};

function TopBar({ onMenuClick, children, activeLabel }: TopBarProps) {
  return (
    <Flex
      as="header"
      position="sticky"
      top={0}
      zIndex={10}
      bg="whiteAlpha.900"
      backdropFilter="saturate(180%) blur(12px)"
      borderBottom="1px solid"
      borderColor="rgba(15, 23, 42, 0.08)"
      px={{ base: 4, md: 8, xl: 12 }}
      py={4}
      justify="space-between"
      align="center"
      gap={4}
    >
      <HStack spacing={3}>
        <IconButton
          display={{ base: "inline-flex", lg: "none" }}
          variant="ghost"
          aria-label="Open navigation"
          icon={<HamburgerIcon />}
          onClick={onMenuClick}
        />
        <Box>
          <Text fontSize="xs" textTransform="uppercase" color="text.muted">
            {activeLabel ?? "Guardrails"}
          </Text>
          <Text fontWeight="medium">{children}</Text>
        </Box>
      </HStack>
      <HStack spacing={4}>
        <Button size="sm" variant="outline">
          Support
        </Button>
        <Button size="sm" colorScheme="brand">
          Deploy changes
        </Button>
      </HStack>
    </Flex>
  );
}
