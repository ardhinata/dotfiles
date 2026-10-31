---
topic: aft-embedding
date: 2026-10-31
source: AFT 0.62.0 source at /tmp/opencode/aftsrc, Magic Context 0.49.25 bundle at ~/.cache/opencode/npm/@cortexkit/opencode-magic-context, local embedding-dimensions proxy
freshness: check 2027-04 (the AFT fingerprint fields and the Magic Context identity may change)
---

# The endpoint URL can carry the vector width, and the width must be in it

## The finding

The vector width can be named per caller in the endpoint URL. The proxy
reads the width from the path and serves that width to that caller. The
proxy and the client use different endpoint forms:

| Endpoint | The proxy serves |
|---|---|
| `http://127.0.0.1:8099/v1` | the default width |
| `http://127.0.0.1:8099/<salt>/v1` | the default width. The salt changes the identity. |
| `http://127.0.0.1:8099/<salt>/<dims>/v1` | `<dims>` floats |

The width must be between 1 and 4096, and it must hold decimal digits only.

## Why the width belongs in the URL, not in a config field

Neither client has a width field. AFT sends a fixed body `{input, model}`
and its semantic config struct holds no width key. Magic Context sends
`{model, input, input_type, truncate}` and its embedding config holds no
width key either. The endpoint URL is the only channel each client has.

## The part that matters: the width must change the identity

A width change leaves the stored rows at the old width unless the identity
changes too. The cosine score of a length mismatch is zero, so the
retrieval lane returns nothing while it looks healthy. A stale row is
worse than a missing row, because it looks present.

The two clients detect a width change differently:

- **AFT** probes the backend and reads the vector width of the probe
  response into its fingerprint (`SemanticIndexFingerprint::from_config`
  takes a `dimension`). AFT also hashes `base_url` into the same
  fingerprint. A width change therefore changes the fingerprint twice
  over, and a mismatch returns `None` from `read_from_disk`, which
  rebuilds. The log line reads `cached semantic index fingerprint
  mismatch, rebuilding without deleting the shared artifact`.
- **Magic Context** has no width field. `getEmbeddingProviderIdentity`
  hashes the provider, the model, the endpoint, the presence of an API
  key, the input type, the document prefix and the truncate value. The
  width is not in that list, and it is not in the `model_id` that names
  the memory rows and the git commit rows. A width change that leaves the
  endpoint alone therefore leaves those rows at the old width.

So for Magic Context the width segment is what makes a width change a
re-embed. That is the reason the width belongs in the URL rather than in a
setting that only the proxy reads.

The chunk rows of Magic Context do carry a `dims` column, and the search
pool filters on `vector.length === queryDimensions`. That filter hides a
width mismatch from the memory lane and the git commit lane, which have no
such column.

## The measured widths

AFT uses 384 and Magic Context uses 512. The A/B on 2026-10-31 found the
two widths equal on every retrieval metric over 62 queries: semantic-only
R@1 26/50 against 27/50 and MRR 0.631 against 0.640, with every exact
McNemar and sign test above p = 0.5. The 384 index is 18.8 percent
smaller.

Magic Context keeps 512 because it has no lexical lane to fall back on.
AFT fuses a lexical lane that carries the weight for identifier and path
queries. A narrower vector costs AFT nothing that the lane cannot cover.

## The proxy must be updated before the clients

An older proxy ignores the path and serves the default width to every
caller. A client that asked for 384 would then store 512 float rows under
a 384 endpoint. Deploy the proxy script and restart the service first,
then change the client config.

## The width check on the reply

A provider can ignore the `dimensions` field and answer with the model
default. The caller stores the reply as it is, so it stores rows of the
wrong width and the failure is silent. The proxy now refuses a 200 reply
that holds vectors of another width with a 502.

Provider-side support for the `dimensions` field on `qwen/qwen3-embedding-8b`
is not uniform. SiliconFlow documents an allowed list that excludes 384.
Nebius and DeepInfra both accept 384 and 512.

## See also

- [Embedding width A/B through the AFT semantic lane](2026-10-31-embedding-width-ab.md)
- [Embedding build tuning: token cap, batch size, and provider routing](2026-10-31-embedding-build-tuning.md)
- `docs/how-to/embedding-dimensions-proxy-deployment.md` — the deployment guide
