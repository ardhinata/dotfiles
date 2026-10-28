# No Progress Stop

Stop when the evidence stops. Report what blocked you. Stop at two. Do not run
a third attempt.

## Two triggers

- **Same failure twice.** The same step fails twice with the same error. A
  different error message counts as new progress.
- **Same hypothesis twice.** Two consecutive probes of one hypothesis add no
  new information. The output text may differ. The finding must not.

Name the hypothesis, and the result that would falsify it, before the first
probe. A second probe with no falsifier hit ends that hypothesis.

A lookup is not a probe. Reading a second file, a second catalog entry, or a
second source to collect facts about a named target is one lookup with several
reads. Stop only when a second lookup at the same target also stops narrowing
the answer.
