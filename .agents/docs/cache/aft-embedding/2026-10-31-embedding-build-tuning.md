---
topic: aft-embedding
date: 2026-10-31
source: AFT 0.62.0 source at /tmp/opencode/aftsrc, local embedding-dimensions proxy, erenmin rebuild logs, OpenRouter provider routing
freshness: check 2027-04 (the provider quota and the AFT build knobs both change)
---

# Embedding build tuning: token cap, batch size, and provider routing

## Question

Which three knobs decide how fast and how reliably an AFT semantic index
builds, and what value does each one hold?

## The three knobs

| Knob | Value | In the index fingerprint? |
|---|---|---|
| `semantic.max_input_tokens` | 480 | **Yes.** `EmbedTextCaps` is a fingerprint field. |
| `semantic.max_batch_size` | 32 | **No.** |
| Provider list on the proxy | `{"only":["nebius","deepinfra"],"allow_fallbacks":true}` | **No.** It is a proxy-side setting. |

A change to the token cap forces a full re-embed of every root. A change
to the batch size or to the provider list does not.

The salt in the `base_url` is a different matter. AFT hashes the whole
`base_url` into the fingerprint. A change to the salt segment therefore
forces a re-embed, even though the proxy drops the salt before the request
reaches the provider. The provider list never appears in the URL, so it
never changes the fingerprint.

## The token cap does not decide the build speed

`max_input_tokens` sets the length of the text embedded for each chunk. It
does not set the number of chunks.

Two rebuilds of the same erenmin corpus, 21,297 chunks each:

| Cap | Build time |
|---|---|
| 640 tokens | 1490 s |
| 480 tokens | 1457 s |

A 25 percent cut in embedded text per chunk bought 2 percent of build
time. Tokens per minute is not the binding constraint here, so the cap is
not a speed knob.

The cap still matters for quality. A smaller chunk carries less context,
which reduces dilution. The live value is 480, lowered from 640 on
2026-10-30.

## The batch size decides whether a build fails

`max_batch_size` sets the number of chunks in one embedding request. The
same erenmin rebuild, same provider quota, two batch sizes:

| Batch | Tokens per request | Result |
|---|---|---|
| 80 rows | about 38,000 | Hit the 25 s build deadline once, plus 6 upstream HTTP 502 resets. |
| 32 rows | about 15,000 | 671 requests, no HTTP 502, no deadline failure. |

Both ran at the same throughput, about 14 chunks per second. The smaller
batch costs no time and removes the failures, so 32 is the value.

The failure mode is worth stating. AFT halves the batch size only after a
request **times out**. A provider that answers HTTP 429 keeps the batch
size. One oversized request can then fail on its own and burn three
retries before the build backs off.

## The provider quota is the wall

The upstream provider enforces a tokens-per-minute quota and answers a
burst with HTTP 429. That quota, not the batch size, is the limit on
throughput. Two concurrent builds give the same aggregate throughput as
one build alone, about 18 embedding requests per minute and 145,000 tokens
per minute in total. Running builds in parallel does not buy speed.

## Provider routing

The proxy names the providers the request may use and lets OpenRouter pick
per request:

```json
{"only": ["nebius", "deepinfra"], "allow_fallbacks": true}
```

The list has no `order`, so OpenRouter selects by price, throughput,
latency, and reliability. It then moves traffic away from the pool that
answers with HTTP 429. SiliconFlow is not in the list.

Both listed providers honour the `dimensions` request parameter at 512
(verified live on 2026-10-31, one request each). SiliconFlow documents an
allowed width list of 64, 128, 256, 512, 768, 1024, 2048, and 4096, so
384 is not available there.

## Source of the numbers

The token cap and batch size figures come from erenmin rebuild logs. The
fingerprint claims come from `SemanticIndexFingerprint::from_config` in
`crates/aft/src/semantic_index.rs`, which copies `dimension` and
`embed_text_caps` and no batch size.

## See also

- [Embedding width A/B through the AFT semantic lane](2026-10-31-embedding-width-ab.md)
- `dot_config/private_cortexkit/aft.jsonc` — the live values, with the
  measurements in the comments
