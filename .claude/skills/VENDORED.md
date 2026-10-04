# Vendored skills

`brag/` and `brag-slim/` are copied from https://github.com/latent-spaces/brag
(MIT, see `brag/LICENSE`) at commit cb89b9f44309b0bf4e3cb89e685fadf80c7999ed (v0.4.0).

They live here so `/brag` works in every Claude Code session on this repo,
including cloud sessions, without running `/plugin install`.

To update:

    git clone --depth 1 https://github.com/latent-spaces/brag /tmp/brag
    rm -rf .claude/skills/brag && cp -a /tmp/brag/skills/brag .claude/skills/brag
    rm -rf .claude/skills/brag-slim && cp -a /tmp/brag/skills/brag-slim .claude/skills/brag-slim
    cp /tmp/brag/LICENSE .claude/skills/brag/LICENSE

Music license: the bundled tracks in `brag/assets/music/` come from ende.app.
Check their terms before using one in a paid ad.
