"use client";

import { STRATA, TREATMENTS, depthToFraction } from "@/lib/treatments";

const W = 560;
const H = 400;
const TOP = 26; // room for the "0 mm — surface" rule
const BOTTOM = 40; // room for the treatment labels
const LEFT = 148; // gutter for stratum names, on one line each
const PLOT_H = H - TOP - BOTTOM;

const y = (mm: number) => TOP + depthToFraction(mm) * PLOT_H;

type Props = {
  activeId: string | null;
  onActivate?: (id: string | null) => void;
  animate?: boolean;
  /** Renders the interactive hit areas. Off for the decorative hero copy. */
  interactive?: boolean;
};

/**
 * The signature element: a cross-section of skin with each treatment drawn as a
 * needle descending to the depth it actually works at. Geometry comes straight
 * from lib/treatments.ts, so the drawing cannot drift from the stated data.
 */
export default function DepthDiagram({
  activeId,
  onActivate,
  animate = false,
  interactive = true,
}: Props) {
  const columnWidth = (W - LEFT - 24) / TREATMENTS.length;

  return (
    <svg
      className={`diagram-svg${animate ? " diagram-anim" : ""}`}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Cross-section of skin showing the depth each treatment works at, from medical peels in the epidermis at 0.06 millimetres down to dermal filler on the periosteum at 8 millimetres."
    >
      {/* Strata bands, alternating tint so the layers read as distinct */}
      {STRATA.map((stratum, i) => {
        const from = i === 0 ? 0 : STRATA[i - 1].to;
        const top = y(from);
        const height = y(stratum.to) - top;
        return (
          <g
            key={stratum.id}
            className="stratum-band"
            style={{ "--i": i } as React.CSSProperties}
          >
            <rect
              x={LEFT}
              y={top}
              width={W - LEFT}
              height={height}
              className={i % 2 === 0 ? "stratum-fill" : "stratum-fill-alt"}
            />
            <line
              x1={LEFT}
              y1={top}
              x2={W}
              y2={top}
              className="stratum-line"
            />
            {/* One line, so a 24px-tall band cannot collide with the next */}
            <text x={0} y={top + 12} className="stratum-label">
              {stratum.label}
              <tspan className="stratum-depth" dx="6">
                {from}–{stratum.to} mm
              </tspan>
            </text>
          </g>
        );
      })}

      {/* Needles */}
      {TREATMENTS.map((t, i) => {
        const cx = LEFT + columnWidth * (i + 0.5);
        const yTop = y(0);
        const yMin = y(t.depthMin);
        const yMax = y(t.depthMax);
        const isActive = activeId === t.id;
        const len = yMax - yTop;

        return (
          <g
            key={t.id}
            className={`needle-group${isActive ? " needle-active" : ""}`}
            style={{ "--i": i } as React.CSSProperties}
            // An SVG <title> would be the natural tooltip here, but React 19
            // hoists <title> as document metadata, which breaks hydration.
            role="img"
            aria-label={`${t.name}: ${t.depthMin} to ${t.depthMax} millimetres, ${t.plane.toLowerCase()}`}
            onMouseEnter={interactive ? () => onActivate?.(t.id) : undefined}
            onMouseLeave={interactive ? () => onActivate?.(null) : undefined}
          >
            {/* Shaft from the surface to the deepest working point */}
            <line
              x1={cx}
              y1={yTop}
              x2={cx}
              y2={yMax}
              className="needle-track needle-draw"
              style={{ "--len": len } as React.CSSProperties}
            />
            {/* The working range — the part that carries the meaning */}
            <line
              x1={cx}
              y1={yMin}
              x2={cx}
              y2={yMax}
              className="needle-work needle-draw"
              style={{ "--len": yMax - yMin } as React.CSSProperties}
            />
            <circle
              cx={cx}
              cy={yMax}
              r={isActive ? 5 : 3.5}
              className="needle-tip needle-pop"
            />
            {/* The depth *range* rather than the maximum: two treatments share
                a max of 1.5 mm, so maxima alone read as a duplicated label. */}
            <text
              x={cx}
              y={H - 22}
              textAnchor="middle"
              className="needle-label needle-text"
            >
              {t.depthMin}–{t.depthMax}
            </text>

            {interactive && (
              /* A generous invisible hit area: the needle itself is 3px wide */
              <rect
                x={cx - columnWidth / 2}
                y={TOP}
                width={columnWidth}
                height={PLOT_H + BOTTOM - 10}
                className="needle-hit"
              />
            )}
          </g>
        );
      })}

      {/* Surface rule sits above everything so it never gets covered */}
      <line x1={LEFT} y1={y(0)} x2={W} y2={y(0)} className="stratum-line" />
      <text x={0} y={y(0) - 8} className="stratum-depth">
        0 mm — surface
      </text>
    </svg>
  );
}
