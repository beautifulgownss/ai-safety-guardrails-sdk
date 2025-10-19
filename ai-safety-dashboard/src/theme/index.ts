import { extendTheme, ThemeConfig } from "@chakra-ui/react";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: false,
};

export const theme = extendTheme({
  config,
  fonts: {
    heading: "var(--font-dm-serif)",
    body: "var(--font-inter)",
  },
  colors: {
    background: {
      canvas: "#FAFAFA",
      raised: "#FFFFFF",
      subtle: "#F3F3F3",
    },
    brand: {
      50: "#F8E8EE",
      100: "#F0D1DE",
      200: "#E2A4C0",
      300: "#D575A3",
      400: "#D06B99",
      500: "#B35C84",
      600: "#964C6F",
      700: "#7A3D5A",
      800: "#5D2E45",
      900: "#412030",
    },
    neutral: {
      50: "#F7F7F7",
      100: "#E8E8E8",
      200: "#D1D1D1",
      300: "#B0B0B0",
      400: "#8F8F8F",
      500: "#706F70",
      600: "#545354",
      700: "#3E3D3F",
      800: "#2A292B",
      900: "#17161A",
    },
  },
  semanticTokens: {
    colors: {
      "surface.base": "background.canvas",
      "surface.card": "background.raised",
      "surface.subtle": "background.subtle",
      "text.muted": "neutral.500",
      "text.default": "neutral.900",
      "accent.base": "brand.400",
      "accent.subtle": "brand.50",
    },
  },
  radii: {
    none: "0px",
    sm: "6px",
    md: "12px",
    lg: "16px",
    xl: "24px",
    "2xl": "32px",
  },
  shadows: {
    xs: "0 2px 6px rgba(15, 23, 42, 0.06)",
    sm: "0 6px 16px rgba(15, 23, 42, 0.08)",
    md: "0 10px 30px rgba(15, 23, 42, 0.10)",
    lg: "0 20px 40px rgba(15, 23, 42, 0.12)",
    outline: "0 0 0 3px rgba(208, 107, 153, 0.28)",
  },
  styles: {
    global: {
      "html, body": {
        bg: "surface.base",
        color: "text.default",
        fontFeatureSettings: '"liga", "kern"',
      },
      body: {
        letterSpacing: "0.01em",
        fontSize: "16px",
      },
      "*::selection": {
        bg: "brand.50",
        color: "text.default",
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        rounded: "lg",
        fontWeight: 600,
        _focusVisible: {
          boxShadow: "outline",
        },
      },
      defaultProps: {
        colorScheme: "brand",
      },
    },
    Input: {
      baseStyle: {
        field: {
          rounded: "lg",
        },
      },
      variants: {
        outline: {
          field: {
            bg: "surface.card",
            borderColor: "neutral.200",
            _hover: { borderColor: "neutral.300" },
            _focusVisible: {
              borderColor: "brand.400",
              boxShadow: "outline",
            },
          },
        },
      },
    },
    Textarea: {
      variants: {
        outline: {
          bg: "surface.card",
          borderColor: "neutral.200",
          rounded: "lg",
          _hover: { borderColor: "neutral.300" },
          _focusVisible: {
            borderColor: "brand.400",
            boxShadow: "outline",
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          rounded: "lg",
          bg: "surface.card",
          shadow: "sm",
          border: "1px solid",
          borderColor: "rgba(15, 23, 42, 0.04)",
        },
      },
    },
    Tabs: {
      baseStyle: {
        tab: {
          rounded: "full",
          _selected: {
            bg: "accent.subtle",
            color: "accent.base",
          },
        },
      },
    },
  },
});

export type AppTheme = typeof theme;
