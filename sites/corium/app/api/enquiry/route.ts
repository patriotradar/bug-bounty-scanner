import { NextResponse } from "next/server";

/**
 * Enquiry endpoint.
 *
 * This validates and acknowledges the enquiry but does not yet deliver it
 * anywhere — see the TODO below. Validation is repeated here rather than
 * trusted from the client, because the client check is a convenience and this
 * one is the actual gate.
 */

const MAX_LENGTHS: Record<string, number> = {
  name: 120,
  email: 254,
  phone: 30,
  treatment: 40,
  window: 40,
  message: 2000,
};

type Enquiry = {
  name: string;
  email: string;
  phone?: string;
  treatment?: string;
  window?: string;
  message?: string;
  consent: boolean;
};

function parse(body: unknown): { data?: Enquiry; error?: string } {
  if (typeof body !== "object" || body === null) {
    return { error: "Malformed request." };
  }
  const raw = body as Record<string, unknown>;

  for (const [field, limit] of Object.entries(MAX_LENGTHS)) {
    const value = raw[field];
    if (typeof value === "string" && value.length > limit) {
      return { error: `The ${field} field is too long.` };
    }
  }

  const name = String(raw.name ?? "").trim();
  const email = String(raw.email ?? "").trim();

  if (name.length < 2) return { error: "A name is required." };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { error: "A valid email address is required." };
  }
  // The checkbox arrives as "on" from FormData, or true from JSON.
  if (raw.consent !== "on" && raw.consent !== true) {
    return { error: "Consent is required to hold these details." };
  }

  return {
    data: {
      name,
      email,
      phone: String(raw.phone ?? "").trim() || undefined,
      treatment: String(raw.treatment ?? "").trim() || undefined,
      window: String(raw.window ?? "").trim() || undefined,
      message: String(raw.message ?? "").trim() || undefined,
      consent: true,
    },
  };
}

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Malformed request." }, { status: 400 });
  }

  const { data, error } = parse(body);
  if (error || !data) {
    return NextResponse.json({ error }, { status: 400 });
  }

  // TODO: deliver the enquiry before this site goes live. Options, in rough
  // order of effort: a transactional email provider (Resend, Postmark) to the
  // clinic inbox; a row in a database; or the clinic's practice-management
  // system if it exposes an API.
  //
  // Patient enquiries are health-adjacent personal data under UK GDPR, so
  // whatever is chosen needs a lawful basis, a retention period matching the
  // six months promised in the consent text, and a processor agreement.
  console.info("[enquiry] received", {
    name: data.name,
    treatment: data.treatment ?? "unspecified",
    at: new Date().toISOString(),
  });

  return NextResponse.json({ ok: true }, { status: 200 });
}
