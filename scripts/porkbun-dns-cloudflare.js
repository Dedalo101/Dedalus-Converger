/**
 * Point dedalo101.com DNS at Cloudflare Pages (Dedalus-Converger).
 *
 * Usage (PowerShell):
 *   $env:PORKBUN_API_KEY = "pk1_..."
 *   $env:PORKBUN_SECRET_API_KEY = "sk1_..."
 *   $env:CLOUDFLARE_PAGES_TARGET = "dedalus-converger.pages.dev"  # optional
 *   node scripts/porkbun-dns-cloudflare.js
 *
 * Dry run:
 *   $env:DRY_RUN = "1"
 *   node scripts/porkbun-dns-cloudflare.js
 *
 * Only apex (@) and www are modified. Subdomains like pb.dedalo101.com are preserved.
 */
const DOMAIN = "dedalo101.com";
const API_BASE = "https://api.porkbun.com/api/json/v3";
const PAGES_TARGET =
  process.env.CLOUDFLARE_PAGES_TARGET || "dedalus-converger.pages.dev";
const DRY_RUN = process.env.DRY_RUN === "1";

function creds() {
  const apikey = process.env.PORKBUN_API_KEY || process.env.PORKBUN_APIKEY;
  const secretapikey =
    process.env.PORKBUN_SECRET_API_KEY || process.env.PORKBUN_SECRETAPIKEY;
  if (!apikey || !secretapikey) {
    throw new Error(
      "Missing PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY environment variables."
    );
  }
  return { apikey, secretapikey };
}

async function porkbun(path, body = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...creds(), ...body }),
  });
  const data = await res.json();
  if (data.status !== "SUCCESS") {
    const err = new Error(data.message || `Porkbun error on ${path}`);
    err.code = data.code;
    err.payload = data;
    throw err;
  }
  return data;
}

async function ping() {
  const data = await porkbun("/ping");
  if (!data.credentialsValid) {
    throw new Error("Porkbun credentials invalid");
  }
  console.log(`Porkbun API OK — caller IP ${data.yourIp}`);
}

async function listRecords() {
  const data = await porkbun(`/dns/retrieve/${DOMAIN}`);
  return data.records || [];
}

function recordName(rec) {
  const name = String(rec.name || "").toLowerCase();
  if (name === "" || name === "@") return "@";
  return name;
}

function isApexOrWww(rec) {
  const name = recordName(rec);
  return name === "@" || name === "www";
}

function isParkingRecord(rec) {
  if (!isApexOrWww(rec)) return false;
  const content = String(rec.content || "").toLowerCase();
  if (rec.type === "CNAME" && content.includes("porkbun.com")) return true;
  if (rec.type === "A" && (content.startsWith("44.230.") || content.startsWith("52.33.")))
    return true;
  if (rec.type === "ALIAS" && content.includes("porkbun")) return true;
  return false;
}

function wantsCloudflare(rec) {
  const target = PAGES_TARGET.toLowerCase();
  const content = String(rec.content || "").toLowerCase().replace(/\.$/, "");
  const name = recordName(rec);
  if (name === "@") {
    return rec.type === "ALIAS" && content === target;
  }
  if (name === "www") {
    return rec.type === "CNAME" && content === target;
  }
  return false;
}

async function deleteRecord(id) {
  if (DRY_RUN) {
    console.log(`  [dry-run] delete ${id}`);
    return;
  }
  await porkbun(`/dns/delete/${DOMAIN}/${id}`);
  console.log(`  deleted ${id}`);
}

async function createRecord(spec) {
  if (DRY_RUN) {
    console.log(
      `  [dry-run] create ${spec.type} ${spec.name || "@"} → ${spec.content}`
    );
    return;
  }
  await porkbun(`/dns/create/${DOMAIN}`, spec);
  console.log(`  created ${spec.type} ${spec.name || "@"} → ${spec.content}`);
}

async function run() {
  await ping();
  const records = await listRecords();
  console.log(`Current records for ${DOMAIN}: ${records.length}`);

  const stale = records.filter(isParkingRecord);
  console.log(`Removing ${stale.length} parking/apex/www record(s)…`);
  for (const rec of stale) {
    console.log(
      `  - ${rec.type} ${recordName(rec)} → ${rec.content} (id ${rec.id})`
    );
    await deleteRecord(rec.id);
  }

  const refreshed = DRY_RUN ? records : await listRecords();
  const hasApex = refreshed.some(wantsCloudflare);
  const hasWww = refreshed.some(
    (r) =>
      recordName(r) === "www" &&
      r.type === "CNAME" &&
      String(r.content).toLowerCase().includes(PAGES_TARGET)
  );

  if (!hasApex) {
    console.log(`Adding apex ALIAS → ${PAGES_TARGET}`);
    await createRecord({
      type: "ALIAS",
      name: "",
      content: PAGES_TARGET,
      ttl: "600",
    });
  }

  if (!hasWww) {
    console.log(`Adding www CNAME → ${PAGES_TARGET}`);
    await createRecord({
      type: "CNAME",
      name: "www",
      content: PAGES_TARGET,
      ttl: "600",
    });
  }

  const finalRecords = DRY_RUN ? refreshed : await listRecords();
  console.log("\nDone. DNS summary:");
  for (const rec of finalRecords) {
    console.log(
      `  ${rec.type.padEnd(6)} ${recordName(rec).padEnd(8)} ${rec.content}`
    );
  }
  console.log(`\nTarget: https://${DOMAIN}/ (propagation: 5–60 min)`);
  console.log("Cloudflare Pages custom domains: dedalo101.com, www.dedalo101.com");
  if (DRY_RUN) console.log("DRY_RUN=1 — no changes were made.");
}

run().catch((err) => {
  console.error(err.message || err);
  if (err.payload) console.error(JSON.stringify(err.payload, null, 2));
  process.exit(1);
});