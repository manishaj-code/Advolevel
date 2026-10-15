import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Source_Serif_4 } from "next/font/google";

import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const sourceSerif = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin"],
  weight: ["600"],
});
const jetbrainsMono = JetBrains_Mono({ variable: "--font-jetbrains-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: { default: "AdvoLevel", template: "%s · AdvoLevel" },
  description: "Your AI executive team.",
};

// Clerk resolves the session in the browser (no `dynamic` prop), so the shell stays prerenderable
// under Cache Components. Authorization is enforced by the API on every request.
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: "#111f38",
          fontFamily: "var(--font-inter)",
          borderRadius: "6px",
        },
      }}
    >
      <html
        lang="en"
        className={`${inter.variable} ${sourceSerif.variable} ${jetbrainsMono.variable} h-full antialiased`}
      >
        <body className="min-h-full">
          <Providers>{children}</Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
