"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { CSSProperties } from "react";

/**
 * Ambient glow that rises over a horizon from one edge of its container.
 *
 * Ported from the Tailwind original: this project has no Tailwind, so the four
 * utility classes (`absolute w-full h-full`, `absolute inset-0 rounded-[100%]`)
 * are expressed as inline styles instead. The props API is unchanged.
 *
 * The element must sit inside a positioned container with `overflow: hidden` —
 * the arcs are scaled past 100% and would otherwise spill onto the page.
 */

const EASE = [0.16, 1, 0.3, 1] as const;
const DURATION = 2;

export type GlowHorizonVariant = "top" | "bottom" | "left" | "right";

const VARIANTS: Record<
  GlowHorizonVariant,
  {
    axis: "x" | "y";
    scaleAxis: "scaleX" | "scaleY";
    enterPct: string;
    restPct: string;
  }
> = {
  top: { axis: "y", scaleAxis: "scaleY", enterPct: "-100%", restPct: "-50%" },
  bottom: { axis: "y", scaleAxis: "scaleY", enterPct: "100%", restPct: "50%" },
  left: { axis: "x", scaleAxis: "scaleX", enterPct: "100%", restPct: "50%" },
  right: { axis: "x", scaleAxis: "scaleX", enterPct: "-100%", restPct: "-50%" },
};

export interface GlowHorizonProps {
  className?: string;
  variant?: GlowHorizonVariant;
  /** Inline styles merged onto the wrapper, for positioning within a parent. */
  style?: CSSProperties;
}

const WRAPPER_STYLE: CSSProperties = {
  position: "absolute",
  width: "100%",
  height: "100%",
  isolation: "isolate",
  // The glow is decoration; it must never intercept clicks on the UI above it.
  pointerEvents: "none",
};

export default function GlowHorizonFM({
  className,
  variant = "top",
  style,
}: GlowHorizonProps) {
  const { axis, scaleAxis, enterPct, restPct } = VARIANTS[variant];

  // framer-motion does not honour prefers-reduced-motion on its own. With it
  // set, the glow renders at its resting position with no entrance rather than
  // sweeping a full-viewport blur across the screen.
  const reduceMotion = useReducedMotion();

  const restState = {
    [axis]: restPct,
    [scaleAxis]: 1,
    opacity: 1,
    filter: "blur(0px)",
  };

  return (
    <motion.div
      className={className}
      style={{ ...WRAPPER_STYLE, ...style }}
      initial={
        reduceMotion
          ? restState
          : {
              [axis]: enterPct,
              [scaleAxis]: 1.5,
              opacity: 0,
              filter: "blur(15px)",
            }
      }
      animate={restState}
      transition={
        reduceMotion ? { duration: 0 } : { duration: DURATION, ease: EASE }
      }
    >
      <Arc
        variant={variant}
        color="#FFFFFF"
        size="132%"
        boxShadow="0px -4px 23px 0px #ffffffb5"
        delay={1.2}
      />
      <Arc
        variant={variant}
        color="#A558FB"
        size="120%"
        initialOffset="10%"
        blur={31}
        delay={0.6}
      />
      <Arc
        variant={variant}
        color="#4922E5"
        size="124%"
        initialOffset="10%"
        blur={21}
        delay={0}
      />
      <Arc
        variant={variant}
        color="#000"
        size="120%"
        initialOffset="10%"
        blur={51}
        delay={0}
      />
    </motion.div>
  );
}

const ARC_STYLE: CSSProperties = {
  position: "absolute",
  inset: 0,
  borderRadius: "100%",
};

function Arc({
  variant,
  color,
  size,
  initialOffset,
  blur,
  boxShadow,
  delay,
}: {
  variant: GlowHorizonVariant;
  color: string;
  size: string;
  initialOffset?: string;
  blur?: number;
  boxShadow?: string;
  delay: number;
}) {
  const scale = parseFloat(size) / 100;
  const { axis, enterPct } = VARIANTS[variant];
  const sign = enterPct.startsWith("-") ? -1 : 1;
  const startPct = initialOffset
    ? `${sign * Math.abs(parseFloat(initialOffset) - 50)}%`
    : undefined;
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      aria-hidden
      style={{
        ...ARC_STYLE,
        scale,
        background: color,
        ...(blur !== undefined && { filter: `blur(${blur}px)` }),
        ...(boxShadow && { boxShadow }),
      }}
      // Same reasoning as the wrapper: the animate target keys depend only on
      // startPct, never on reduceMotion, so a post-hydration flip cannot strand
      // the arc at its entry offset. Only the transition varies.
      initial={startPct ? { [axis]: reduceMotion ? 0 : startPct } : false}
      animate={startPct ? { [axis]: 0 } : undefined}
      transition={
        reduceMotion
          ? { duration: 0 }
          : { duration: DURATION, ease: EASE, delay }
      }
    />
  );
}
