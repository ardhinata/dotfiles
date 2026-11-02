---
description: General variant pinned to opencode-go/glm-5.3-flash. Same general-purpose role as the built-in general agent, with a fixed model.
mode: subagent
model: opencode-go/glm-5.3-flash#high
permissions:
  - { action: question, resource: "*", effect: deny }
  - { action: subagent, resource: "*", effect: deny }
