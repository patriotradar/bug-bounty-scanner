import Reveal from "./Reveal";

/**
 * This section is numbered by day because the sequence is real: the gap between
 * consultation and treatment is a deliberate cooling-off period, and the review
 * date is fixed relative to it. The numbers carry information the reader needs.
 */
const STEPS = [
  {
    day: "Day 0",
    title: "Consultation",
    body: "Forty-five minutes with the clinician who would treat you. Medical history, what is bothering you, and an honest read on whether anything here will help. £50, redeemed against treatment if you go ahead.",
  },
  {
    day: "Days 1–13",
    title: "Reflection period",
    body: "You go away with a written plan, the cost, and the risks specific to you. Nothing is booked during this window. If you have questions, you email the clinician directly rather than a booking line.",
  },
  {
    day: "Day 14",
    title: "Treatment",
    body: "Earliest date we will treat a new patient. Consent is taken again on the day, because consent given a fortnight ago to a plan you have since had second thoughts about is not consent.",
  },
  {
    day: "Day 28",
    title: "Review",
    body: "Included, not an upsell. We photograph under the same lighting as day 0 and adjust if something has settled unevenly. Most reviews end with no further treatment.",
  },
];

export default function Pathway() {
  return (
    <section className="shell band" id="pathway">
      <Reveal className="head">
        <div>
          <p className="eyebrow">What happens</p>
          <h2 className="display-lg head-title">
            Twenty-eight days, start to review
          </h2>
        </div>
        <p className="prose">
          The fortnight between consultation and treatment is not a scheduling
          artefact. It is there so that a decision made in the room can be
          reconsidered outside it.
        </p>
      </Reveal>

      <ol className="path-list">
        {STEPS.map((step, i) => (
          <Reveal as="li" key={step.day} className="path-item" delay={i * 70}>
            <div className="path-marker" aria-hidden="true">
              <span className="path-dot" />
              {i < STEPS.length - 1 && <span className="path-stem" />}
            </div>
            <div>
              <span className="path-day">{step.day}</span>
              <h3 className="path-title">{step.title}</h3>
              <p className="path-body">{step.body}</p>
            </div>
          </Reveal>
        ))}
      </ol>
    </section>
  );
}
