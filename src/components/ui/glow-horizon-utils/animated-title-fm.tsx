"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { CSSProperties } from "react";

/**
 * Staggered title reveal, written to partner GlowHorizonFM.
 *
 * Timing is deliberate rather than arbitrary: the glow's white cap arc lands at
 * 1.2s, so the words begin at 0.9s and resolve just after it. The two read as
 * one sequence instead of two animations that happen to overlap.
 *
 * The original component this was written for was not supplied, so this is a
 * reconstruction against the demo's `open` prop.
 */

const EASE = [0.16, 1, 0.3, 1] as const;
const START_DELAY = 0.9;
const STAGGER = 0.08;

export interface AnimatedTitleProps {
  /** Drives the reveal. Kept from the original demo's API. */
  open?: boolean;
  title?: string;
  subtitle?: string;
  className?: string;
}

const WRAP: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 18,
  textAlign: "center",
  padding: "0 24px",
};

const LINE: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  justifyContent: "center",
  gap: "0 0.28em",
  margin: 0,
  fontSize: "clamp(30px, 6vw, 62px)",
  lineHeight: 1.06,
  letterSpacing: "-0.035em",
  fontWeight: 700,
  color: "#f4f2ff",
};

/* Each word sits in a clipping span so it rises out of a hard edge rather than
   simply fading — the mask is what makes the motion read as deliberate. */
const CLIP: CSSProperties = {
  display: "inline-block",
  overflow: "hidden",
  paddingBottom: "0.08em",
};

export function AnimatedTitleFM({
  open = true,
  title = "ScopeGuard AI",
  subtitle,
  className,
}: AnimatedTitleProps) {
  const reduceMotion = useReducedMotion();
  const words = title.split(" ");

  return (
    <div className={className} style={WRAP}>
      {/* Words are separate flex children spaced by `gap`, so the text nodes
          carry no whitespace and the accessible name would read as one run-on
          word. aria-label restores the real string for assistive tech. */}
      <h1 style={LINE} aria-label={title}>
        {words.map((word, i) => (
          <span key={`${word}-${i}`} style={CLIP} aria-hidden="true">
            {/* `animate` must always carry the same property set. useReducedMotion
                is false during SSR and flips true after hydration; if `y` were
                dropped from the target on that flip it would stay pinned at
                110% behind the clip mask and the title would never appear. Only
                the transition changes. */}
            <motion.span
              style={{ display: "inline-block", willChange: "transform" }}
              initial={{ y: reduceMotion ? "0%" : "110%", opacity: 0 }}
              animate={open ? { y: "0%", opacity: 1 } : undefined}
              transition={
                reduceMotion
                  ? { duration: 0.2, delay: 0 }
                  : {
                      duration: 1.1,
                      ease: EASE,
                      delay: START_DELAY + i * STAGGER,
                    }
              }
            >
              {word}
            </motion.span>
          </span>
        ))}
      </h1>

      {subtitle && (
        <motion.p
          style={{
            margin: 0,
            maxWidth: "46ch",
            fontSize: "clamp(14px, 1.5vw, 17px)",
            lineHeight: 1.6,
            color: "rgba(226, 222, 245, 0.72)",
          }}
          initial={{ opacity: 0, y: reduceMotion ? 0 : 12 }}
          animate={open ? { opacity: 1, y: 0 } : undefined}
          transition={
            reduceMotion
              ? { duration: 0.2, delay: 0 }
              : {
                  duration: 0.9,
                  ease: EASE,
                  delay: START_DELAY + words.length * STAGGER + 0.1,
                }
          }
        >
          {subtitle}
        </motion.p>
      )}
    </div>
  );
}

export default AnimatedTitleFM;
