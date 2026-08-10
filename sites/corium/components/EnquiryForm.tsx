"use client";

import { useRef, useState } from "react";
import Reveal from "./Reveal";
import { TREATMENTS } from "@/lib/treatments";

type Errors = Partial<Record<string, string>>;

const CONTACT_WINDOWS = [
  "Weekday mornings",
  "Weekday afternoons",
  "Weekday evenings",
  "Saturday",
];

function validate(data: FormData): Errors {
  const errors: Errors = {};
  const name = String(data.get("name") ?? "").trim();
  const email = String(data.get("email") ?? "").trim();
  const phone = String(data.get("phone") ?? "").trim();

  if (name.length < 2) {
    errors.name = "Enter your name so we know who we are replying to.";
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter an email address we can reply to, like you@example.com.";
  }
  // Deliberately loose: UK numbers get written a dozen different ways.
  if (phone && !/^[\d\s+()-]{7,20}$/.test(phone)) {
    errors.phone = "Enter a phone number using digits, spaces and + only.";
  }
  if (!data.get("consent")) {
    errors.consent = "We need your permission before we can hold your details.";
  }
  return errors;
}

export default function EnquiryForm() {
  const formRef = useRef<HTMLFormElement>(null);
  const [errors, setErrors] = useState<Errors>({});
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "failed">(
    "idle",
  );

  // Errors appear only after a field has been left or the form submitted —
  // never while someone is still typing.
  function handleBlur(event: React.FocusEvent<HTMLFormElement>) {
    const field = event.target.getAttribute("name");
    if (!field || !formRef.current) return;
    const found = validate(new FormData(formRef.current));
    setErrors((prev) => ({ ...prev, [field]: found[field] }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const found = validate(data);
    setErrors(found);

    const firstInvalid = Object.keys(found)[0];
    if (firstInvalid) {
      // Move focus to the first problem so keyboard and screen reader users
      // are not left hunting for it.
      form.querySelector<HTMLElement>(`[name="${firstInvalid}"]`)?.focus();
      return;
    }

    setStatus("sending");
    try {
      const response = await fetch("/api/enquiry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.fromEntries(data)),
      });
      setStatus(response.ok ? "sent" : "failed");
    } catch {
      setStatus("failed");
    }
  }

  if (status === "sent") {
    return (
      <div className="enq-done" role="status">
        <svg
          className="enq-done-mark"
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="m8 12.5 2.5 2.5L16 9.5" strokeLinecap="round" />
        </svg>
        <h3 className="display-sm">Enquiry received</h3>
        <p className="prose">
          We reply to every enquiry within one working day, from the clinician
          rather than a booking service. If it is urgent, call 01225 000 000.
        </p>
      </div>
    );
  }

  return (
    <form
      ref={formRef}
      className="enq-form"
      onSubmit={handleSubmit}
      onBlur={handleBlur}
      noValidate
    >
      <div className={`field${errors.name ? " field-invalid" : ""}`}>
        <label className="field-label" htmlFor="name">
          Name<span className="field-req">*</span>
        </label>
        <input
          className="field-input"
          id="name"
          name="name"
          type="text"
          autoComplete="name"
          aria-describedby={errors.name ? "name-error" : undefined}
          aria-invalid={Boolean(errors.name)}
        />
        {errors.name && (
          <p className="field-error" id="name-error" role="alert">
            {errors.name}
          </p>
        )}
      </div>

      <div className="field-row">
        <div className={`field${errors.email ? " field-invalid" : ""}`}>
          <label className="field-label" htmlFor="email">
            Email<span className="field-req">*</span>
          </label>
          <input
            className="field-input"
            id="email"
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            aria-describedby={errors.email ? "email-error" : undefined}
            aria-invalid={Boolean(errors.email)}
          />
          {errors.email && (
            <p className="field-error" id="email-error" role="alert">
              {errors.email}
            </p>
          )}
        </div>

        <div className={`field${errors.phone ? " field-invalid" : ""}`}>
          <label className="field-label" htmlFor="phone">
            Phone
          </label>
          <input
            className="field-input"
            id="phone"
            name="phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            aria-describedby={errors.phone ? "phone-error" : "phone-hint"}
            aria-invalid={Boolean(errors.phone)}
          />
          {errors.phone ? (
            <p className="field-error" id="phone-error" role="alert">
              {errors.phone}
            </p>
          ) : (
            <p className="field-hint" id="phone-hint">
              Optional
            </p>
          )}
        </div>
      </div>

      <div className="field">
        <label className="field-label" htmlFor="treatment">
          What are you considering?
        </label>
        <select className="field-select" id="treatment" name="treatment" defaultValue="">
          <option value="">I am not sure yet</option>
          {TREATMENTS.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
        <p className="field-hint">
          Not sure is a perfectly good answer — the consultation exists to work
          that out.
        </p>
      </div>

      <div className="field">
        <label className="field-label" htmlFor="window">
          Best time to reach you
        </label>
        <select className="field-select" id="window" name="window" defaultValue="">
          <option value="">No preference</option>
          {CONTACT_WINDOWS.map((w) => (
            <option key={w} value={w}>
              {w}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label className="field-label" htmlFor="message">
          Anything you would like us to know
        </label>
        <textarea
          className="field-textarea"
          id="message"
          name="message"
          rows={4}
        />
        <p className="field-hint">
          Please do not include detailed medical history here. We take that
          securely at consultation.
        </p>
      </div>

      <div className={`field${errors.consent ? " field-invalid" : ""}`}>
        <div className="field-consent">
          <input
            className="field-checkbox"
            id="consent"
            name="consent"
            type="checkbox"
            aria-describedby={errors.consent ? "consent-error" : undefined}
            aria-invalid={Boolean(errors.consent)}
          />
          <label className="field-consent-text" htmlFor="consent">
            I agree that Corium may hold my details in order to reply to this
            enquiry. We do not add enquiries to a marketing list, and we delete
            details that do not become patient records after six months.
            <span className="field-req">*</span>
          </label>
        </div>
        {errors.consent && (
          <p className="field-error" id="consent-error" role="alert">
            {errors.consent}
          </p>
        )}
      </div>

      <div className="form-status" aria-live="polite">
        {status === "failed" && (
          <span className="form-status-error">
            The enquiry did not send. Try again, or call 01225 000 000.
          </span>
        )}
      </div>

      <div>
        <button
          className="btn btn-primary"
          type="submit"
          disabled={status === "sending"}
        >
          {status === "sending" ? "Sending…" : "Send enquiry"}
        </button>
      </div>
    </form>
  );
}
