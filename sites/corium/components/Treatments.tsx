"use client";

import { useState } from "react";
import DepthDiagram from "./DepthDiagram";
import Reveal from "./Reveal";
import { TREATMENTS } from "@/lib/treatments";

export default function Treatments() {
  const [active, setActive] = useState<string | null>(TREATMENTS[0].id);
  const activeTreatment = TREATMENTS.find((t) => t.id === active);

  return (
    <section className="shell band" id="treatments">
      <Reveal className="head">
        <div>
          <p className="eyebrow">Treatments</p>
          <h2 className="display-lg head-title">
            Six treatments, six different depths
          </h2>
        </div>
        <p className="prose">
          Prices start from the figures shown and are confirmed in writing after
          your consultation, never before. Select a treatment to see where it
          works and how long it lasts.
        </p>
      </Reveal>

      <div className="tx-layout">
        <ul className="tx-list">
          {TREATMENTS.map((t) => {
            const isActive = active === t.id;
            return (
              <li
                key={t.id}
                className={`tx-item${isActive ? " tx-item-active" : ""}`}
              >
                <button
                  type="button"
                  className="tx-row"
                  aria-expanded={isActive}
                  aria-controls={`tx-detail-${t.id}`}
                  onClick={() => setActive(isActive ? null : t.id)}
                  onMouseEnter={() => setActive(t.id)}
                  onFocus={() => setActive(t.id)}
                >
                  <span className="tx-name">{t.name}</span>
                  <span className="tx-price">from £{t.from}</span>

                  <span className="tx-meta">
                    <span className="datum-strong">
                      {t.depthMin} – {t.depthMax} mm
                    </span>
                    <span className="datum">{t.plane}</span>
                  </span>
                </button>

                <div
                  className="tx-detail"
                  id={`tx-detail-${t.id}`}
                  aria-hidden={!isActive}
                >
                  <div className="tx-detail-inner">
                    <div className="tx-detail-body">
                      <p>{t.summary}</p>
                      <div className="tx-spec">
                        <div className="tx-spec-item">
                          <span className="tx-spec-key">Onset</span>
                          <span className="tx-spec-val">{t.onset}</span>
                        </div>
                        <div className="tx-spec-item">
                          <span className="tx-spec-key">Lasts</span>
                          <span className="tx-spec-val">{t.duration}</span>
                        </div>
                        <div className="tx-spec-item">
                          <span className="tx-spec-key">Downtime</span>
                          <span className="tx-spec-val">{t.downtime}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>

        <Reveal className="tx-aside" delay={80}>
          <div className="diagram">
            <div className="diagram-head">
              <p className="eyebrow">Fig. 2 — Selected plane</p>
              <p className="datum">{activeTreatment?.plane ?? "None selected"}</p>
            </div>

            <DepthDiagram activeId={active} onActivate={setActive} interactive />

            <div className="diagram-foot">
              <p className="datum">Highlighted needle marks the active choice</p>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
