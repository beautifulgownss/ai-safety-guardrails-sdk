import type { Metadata } from "next";
import { DM_Serif_Display, Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const serif = DM_Serif_Display({
  variable: "--font-dm-serif",
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AI Safety Guardrails Dashboard",
  description:
    "Operational dashboard for AI safety guardrails: playground, benchmarks, observability, and policy controls.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${serif.variable} ${inter.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
