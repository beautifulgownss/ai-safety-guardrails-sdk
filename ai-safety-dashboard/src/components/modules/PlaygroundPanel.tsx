"use client";

import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  Divider,
  Flex,
  FormControl,
  FormLabel,
  HStack,
  SimpleGrid,
  Stack,
  Tag,
  Text,
  Textarea,
  VStack,
  chakra,
  shouldForwardProp,
} from "@chakra-ui/react";
import { motion } from "framer-motion";
import { ReactNode, useMemo, useState } from "react";

const MotionBox = chakra(motion.div, {
  shouldForwardProp: (prop) =>
    shouldForwardProp(prop) || prop === "transition" || prop === "variants",
});

type GuardOption = {
  id: string;
  label: string;
  description: string;
  enabled: boolean;
};

type ViolationSpan = {
  id: string;
  label: string;
  severity: "low" | "medium" | "high";
  rationale: string;
  start: number;
  end: number;
};

const initialGuards: GuardOption[] = [
  {
    id: "privacy",
    label: "Privacy Redaction",
    description: "Masks PII such as emails, phone numbers, and addresses.",
    enabled: true,
  },
  {
    id: "toxicity",
    label: "Toxicity Filter",
    description: "Blocks disallowed harassment, violence and hateful content.",
    enabled: true,
  },
  {
    id: "jailbreak",
    label: "Jailbreak Shield",
    description: "Detects prompt injections and jailbreak attempts.",
    enabled: true,
  },
  {
    id: "compliance",
    label: "Compliance",
    description: "Enforces region specific policy carve-outs.",
    enabled: false,
  },
];

const demoViolations: ViolationSpan[] = [
  {
    id: "1",
    label: "Privacy Leak",
    severity: "high",
    rationale: "Detected email address leaked from sandbox data.",
    start: 52,
    end: 64,
  },
  {
    id: "2",
    label: "Toxicity",
    severity: "medium",
    rationale: "Language flagged at toxicity score > 0.62 threshold.",
    start: 118,
    end: 127,
  },
];

const responseTemplate =
  "Thanks for reaching out! You can email me at support@aurora.ai and I will escalate. "\
  + "That idea sounds kind of dumb though, maybe rethink your approach next time.";

export function PlaygroundPanel() {
  const [prompt, setPrompt] = useState(
    "Draft a follow-up note to the enterprise customer about the security update.",
  );
  const [modelOutput, setModelOutput] = useState(responseTemplate);
  const [guards, setGuards] = useState(initialGuards);
  const [isRunning, setIsRunning] = useState(false);
  const [violations, setViolations] = useState<ViolationSpan[]>(demoViolations);

  const highlightedOutput = useMemo(
    () => buildHighlightedOutput(modelOutput, violations),
    [modelOutput, violations],
  );

  const toggleGuard = (id: string) => {
    setGuards((prev) =>
      prev.map((guard) =>
        guard.id === id ? { ...guard, enabled: !guard.enabled } : guard,
      ),
    );
  };

  const runSimulation = () => {
    setIsRunning(true);
    // Simulate a network round-trip; in production this would call the FastAPI backend.
    setTimeout(() => {
      // Create a playful variant when fewer guards are enabled.
      const enabledGuards = guards.filter((guard) => guard.enabled).length;
      if (enabledGuards <= 2) {
        setModelOutput(
          "Sure, here is everything including raw credentials: admin@aurora.ai / supersafe!\nJust don't tell anyone. Also, your idea was terrible.",
        );
        setViolations([
          {
            id: "privacy-2",
            label: "Credential Leak",
            severity: "high",
            rationale: "Model emitted authentication secrets.",
            start: 41,
            end: 67,
          },
          {
            id: "toxicity-2",
            label: "Toxic Language",
            severity: "medium",
            rationale: "Tone violates respectful-comms policy clause 4.b.",
            start: 109,
            end: 117,
          },
        ]);
      } else {
        setModelOutput(responseTemplate);
        setViolations(demoViolations);
      }
      setIsRunning(false);
    }, 550);
  };

  return (
    <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={6}>
      <Stack spacing={6}>
        <Card shadow="sm">
          <CardHeader>
            <VStack align="stretch" spacing={1}>
              <Text fontSize="lg" fontWeight="semibold">
                Prompt playground
              </Text>
              <Text color="text.muted">
                Iterate on prompts while instant guardrail checks keep you out of
                trouble.
              </Text>
            </VStack>
          </CardHeader>
          <CardBody as={Stack} spacing={4}>
            <FormControl>
              <FormLabel>Prompt</FormLabel>
              <Textarea
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                minH="140px"
                placeholder="What question should the AI handle?"
              />
            </FormControl>
            <HStack justify="flex-end">
              <Button
                onClick={runSimulation}
                isLoading={isRunning}
                loadingText="Evaluating"
                colorScheme="brand"
              >
                Run guard stack
              </Button>
            </HStack>
          </CardBody>
        </Card>

        <Card shadow="sm">
          <CardHeader pb={2}>
            <Text fontSize="lg" fontWeight="semibold">
              Guard toggles
            </Text>
          </CardHeader>
          <CardBody>
            <Stack spacing={4}>
              {guards.map((guard) => (
                <Flex
                  key={guard.id}
                  align="flex-start"
                  justify="space-between"
                  gap={4}
                >
                  <Box flex="1">
                    <Text fontWeight="medium">{guard.label}</Text>
                    <Text color="text.muted" fontSize="sm">
                      {guard.description}
                    </Text>
                  </Box>
                  <Checkbox
                    size="lg"
                    colorScheme="brand"
                    isChecked={guard.enabled}
                    onChange={() => toggleGuard(guard.id)}
                    aria-label={`Toggle ${guard.label}`}
                  />
                </Flex>
              ))}
            </Stack>
          </CardBody>
        </Card>
      </Stack>

      <Card shadow="md">
        <CardHeader>
          <HStack justify="space-between" align="center">
            <VStack align="stretch" spacing={0}>
              <Text fontSize="lg" fontWeight="semibold">
                Output review
              </Text>
              <Text fontSize="sm" color="text.muted">
                Violations are highlighted inline for rapid triage.
              </Text>
            </VStack>
            <Tag colorScheme="brand" variant="subtle" borderRadius="full">
              {violations.length} detections
            </Tag>
          </HStack>
        </CardHeader>
        <Divider />
        <CardBody as={Stack} spacing={6}>
          <Stack spacing={3}>
            <Text fontSize="sm" textTransform="uppercase" color="text.muted">
              Generated response
            </Text>
            <MotionBox
              bg="surface.subtle"
              rounded="xl"
              px={5}
              py={4}
              transition={{ duration: 0.2 }}
              _hover={{ shadow: "sm" }}
            >
              <Text lineHeight="tall">{highlightedOutput}</Text>
            </MotionBox>
          </Stack>

          <Stack spacing={4}>
            <Text fontSize="sm" textTransform="uppercase" color="text.muted">
              Violations
            </Text>
            <Stack spacing={4}>
              {violations.map((violation) => (
                <Box
                  key={violation.id}
                  p={4}
                  rounded="lg"
                  bg="surface.subtle"
                  borderLeft="3px solid"
                  borderColor={severityColor(violation.severity)}
                >
                  <HStack justify="space-between">
                    <Text fontWeight="medium">{violation.label}</Text>
                    <Tag
                      size="sm"
                      borderRadius="full"
                      bg={severityColor(violation.severity)}
                      color="white"
                    >
                      {violation.severity.toUpperCase()}
                    </Tag>
                  </HStack>
                  <Text color="text.muted" fontSize="sm" mt={2}>
                    {violation.rationale}
                  </Text>
                </Box>
              ))}
            </Stack>
          </Stack>
        </CardBody>
      </Card>
    </SimpleGrid>
  );
}

function severityColor(level: ViolationSpan["severity"]) {
  switch (level) {
    case "high":
      return "brand.400";
    case "medium":
      return "brand.200";
    case "low":
    default:
      return "neutral.200";
  }
}

function buildHighlightedOutput(
  text: string,
  spans: ViolationSpan[],
): ReactNode {
  if (!spans.length) return text;
  const segments: Array<{ text: string; highlighted: boolean; id: string }> =
    [];
  let cursor = 0;
  const ordered = [...spans].sort((a, b) => a.start - b.start);

  ordered.forEach((span, index) => {
    if (cursor < span.start) {
      segments.push({
        text: text.slice(cursor, span.start),
        highlighted: false,
        id: `plain-${index}-${cursor}`,
      });
    }
    segments.push({
      text: text.slice(span.start, span.end),
      highlighted: true,
      id: span.id,
    });
    cursor = span.end;
  });

  if (cursor < text.length) {
    segments.push({
      text: text.slice(cursor),
      highlighted: false,
      id: `plain-end`,
    });
  }

  return segments.map((segment) =>
    segment.highlighted ? (
      <Box
        as="mark"
        key={segment.id}
        color="accent.base"
        bg="accent.subtle"
        rounded="md"
        px="1"
        mx="1px"
      >
        {segment.text}
      </Box>
    ) : (
      <Text as="span" key={segment.id}>
        {segment.text}
      </Text>
    ),
  );
}
