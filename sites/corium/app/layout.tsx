import type { Metadata, Viewport } from "next";
import { Bodoni_Moda, Instrument_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

/**
 * Fonts are self-hosted by next/font: no request to a third-party origin, no
 * flash of invisible text, and metric fallbacks are generated so the type
 * swapping in does not shift layout.
 */
const bodoni = Bodoni_Moda({
  subsets: ["latin"],
  weight: ["400", "500"],
  style: ["normal", "italic"],
  display: "swap",
  variable: "--font-bodoni",
});

const instrument = Instrument_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
  variable: "--font-sans",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
  variable: "--font-mono-plex",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://corium.clinic"),
  title: {
    default: "Corium — Doctor-led aesthetics clinic in Bath",
    template: "%s — Corium",
  },
  description:
    "A doctor-led aesthetics clinic in Bath. Treatments planned at measured depths, with a two-week reflection period between consultation and treatment.",
  openGraph: {
    title: "Corium — Doctor-led aesthetics clinic in Bath",
    description:
      "Treatments planned at measured depths, with a two-week reflection period between consultation and treatment.",
    locale: "en_GB",
    type: "website",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // No maximumScale or userScalable: pinch zoom stays available.
  themeColor: "#eef1ee",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en-GB"
      className={`${bodoni.variable} ${instrument.variable} ${plexMono.variable}`}
      // The inline script below adds a `js` class to this element before React
      // hydrates, which is by definition a server/client difference. Suppressed
      // here so it does not surface as a hydration error.
      suppressHydrationWarning
    >
      <body>
        {/*
          Marks the document as JavaScript-capable before the page paints.
          Scroll-reveal hides content with opacity, so that hiding must only
          ever apply when something is guaranteed to reveal it again — without
          this flag a JS failure would leave most of the page blank.
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `document.documentElement.classList.add('js')`,
          }}
        />
        <a className="skip-link" href="#main">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
