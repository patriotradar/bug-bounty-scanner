"use client";

import { useState } from "react";
import DepthDiagram from "./DepthDiagram";

export default function Hero() {
  const [active, setActive] = useState<string | null>(null);

  return (
    <section className="shell hero" id="top">
      <div className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">Doctor-led aesthetics · Bath</p>

          <h1 className="display-xl hero-title">
            Every millimetre
            <br />
            is a <span className="hero-title-em">decision</span>.
          </h1>

          <p className="lede hero-lede">
            Filler sits on bone at eight millimetres. A peel works in the top
            tenth of one. The difference between a good result and an obvious
            one is knowing exactly which plane you are treating — and declining
            the treatments that would not help you.
          </p>

          <div className="hero-actions">
            <a className="btn btn-primary" href="#enquire">
              Request a consultation
            </a>
            <a className="btn btn-quiet" href="#treatments">
              See what we treat
            </a>
          </div>

          <p className="hero-note">
            <span className="datum-strong">£50</span>
            <span className="datum">
              consultation, redeemed against treatment · 14-day reflection
              period before anything is booked
            </span>
          </p>
        </div>

        <div className="diagram">
          <div className="diagram-head">
            <p className="eyebrow">Fig. 1 — Treatment depth</p>
            <p className="datum">n = 6</p>
          </div>

          <DepthDiagram
            activeId={active}
            onActivate={setActive}
            animate
            interactive
          />

          <div className="diagram-foot">
            <p className="datum">Depth below skin surface, in millimetres</p>
            <p className="datum">Vertical axis is non-linear</p>
          </div>
        </div>
      </div>
    </section>
  );
}
