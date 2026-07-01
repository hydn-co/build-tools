# setup-npm-private

Org-wide auth for installing **private** `@hydn-co/*` npm packages from GitHub
Packages (the `substrate` **fetch** / **fetch-gen** forks) in CI and Docker builds.
Reuses the same `hydn-substrate-read` GitHub App as [`setup-go-private`](../setup-go-private);
per-repo footprint is a single step plus one `NODE_AUTH_TOKEN` line.

## Why this exists

GitHub Packages are read over the npm registry, not git. A workflow's default
`GITHUB_TOKEN` can only read packages published by its **own** repo, so any repo
that installs a package published by a *different* hydn-co repo (e.g. mesh-core /
control installing `@hydn-co/fetch` from `substrate`) can't `npm ci` without extra
credentials. Making those packages **Internal** so `GITHUB_TOKEN` works exposes
them to every repo in the org — they should stay **Private**. This action mints a
short-lived **GitHub App installation token** with `Packages: read`, so `npm ci`
reads private packages without over-broad visibility and without a long-lived PAT.

## One-time org setup

Shared with `setup-go-private` — the same `hydn-substrate-read` App and the same
org secrets (`MESH_MODULES_APP_CLIENT_ID`, `MESH_MODULES_APP_KEY`). The only
addition for npm is granting the App **Repository permission → Packages: Read**
(alongside its existing `Contents: Read`), and keeping it installed on `substrate`
plus every repo that consumes a private package. The installation token is
auto-rotating (≈1h), centrally revocable, and auditable.

## CI usage (npm install / build)

`setup-node`'s `registry-url` writes the `~/.npmrc` `${NODE_AUTH_TOKEN}` reference;
this action supplies the token as a step output. Add it **after** `setup-node`, then
point the reading step's `NODE_AUTH_TOKEN` at the output:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: "lts/*"
    registry-url: "https://npm.pkg.github.com"
    scope: "@hydn-co"

- id: npmauth
  uses: hydn-co/build-tools/.github/actions/setup-npm-private@main
  with:
    client-id: ${{ secrets.MESH_MODULES_APP_CLIENT_ID }}
    private-key: ${{ secrets.MESH_MODULES_APP_KEY }}

- run: npm ci
  env:
    NODE_AUTH_TOKEN: ${{ steps.npmauth.outputs.token }}
```

The committed project `.npmrc` only needs to map the scope
(`@hydn-co:registry=https://npm.pkg.github.com`).

### Publishing your own package in the same job

A `Packages: read` token deliberately **cannot publish**. If the same job also runs
`npm publish` for a package your repo owns, leave that step on the built-in token —
it has `packages: write` for your own repo:

```yaml
- run: npm publish
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Docker builds (BuildKit secret, never a build-arg)

`setup-npm-private` exports the token as `GH_PACKAGES_TOKEN`. Forward it to the
image build via `build-app`'s `build-secrets` input:

```yaml
- id: npmauth
  uses: hydn-co/build-tools/.github/actions/setup-npm-private@main
  with:
    client-id: ${{ secrets.MESH_MODULES_APP_CLIENT_ID }}
    private-key: ${{ secrets.MESH_MODULES_APP_KEY }}

- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: portald
    arch: amd64
    semver: ${{ inputs.semver }}
    registry: ghcr.io
    org: hydn-co
    build-secrets: id=npmtoken,env=GH_PACKAGES_TOKEN
```

Dockerfile (in the `npm ci` stage):

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=secret,id=npmtoken \
    sh -c 'if [ -f /run/secrets/npmtoken ]; then \
             printf "@hydn-co:registry=https://npm.pkg.github.com/\n//npm.pkg.github.com/:_authToken=%s\n" "$(cat /run/secrets/npmtoken)" >> "$HOME/.npmrc"; \
           fi; \
           npm ci --cache /root/.npm --prefer-offline --no-audit --no-fund'
```

## Local dev

No action needed — org members with `substrate` access can read the private
packages via their `gh` login:

```bash
npm run mesh:auth   # writes your gh token to ~/.npmrc for npm.pkg.github.com
```
