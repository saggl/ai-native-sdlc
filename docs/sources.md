# Sources and provenance

Consulted 2026-10-03:

- [Anthropic: The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook),
  including the Markdown copy supplied by the repository owner. Basis for committed
  artifacts, human decisions, feedback loops, review and maintenance feeding new intent.
- [Claude Code plugins](https://code.claude.com/docs/en/plugins) and
  [create a plugin](https://code.claude.com/docs/en/plugins/create): packaging and local testing.
- [Create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces): distribution.
- [Skills](https://code.claude.com/docs/en/skills): namespaced commands, supporting resources
  and the plugin root substitution.
- [Plugin commands](https://code.claude.com/docs/en/plugins/cli-reference) and
  [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference): install,
  update and version behavior.

This is an independent implementation, not an Anthropic product. Templates, command names,
per-change folders, local state, fingerprints and workflow routing are local design choices.
The full article, its artwork and its worked examples are not redistributed. The small
legacy examples in this repository are illustrative draft artifacts, not approved work.
