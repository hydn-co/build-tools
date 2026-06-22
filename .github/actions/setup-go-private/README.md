# setup-go-private

Org-wide auth for fetching **private** `github.com/hydn-co/*` Go modules (the
`substrate` infra layer and the private `mesh-*` modules) from CI and Docker
builds. One GitHub App + one composite action; per-repo footprint is a single step.

## Why this exists

Go modules are fetched as source over git. A workflow's default `GITHUB_TOKEN`
can only read its **own** repo, so any repo that imports a *different* private
hydn-co module can't `go mod download` without extra credentials. This action
mints a short-lived **GitHub App installation token** with `Contents: read`,
points git at it, and sets `GOPRIVATE` (which bypasses `proxy.golang.org` and
`sum.golang.org` for those modules — `go.sum` still pins integrity hashes).

## One-time org setup (manual, GitHub UI)

1. **Create a GitHub App** (Org → Settings → Developer settings → GitHub Apps → New):
   - Name: `mesh-modules-read`
   - Repository permissions: **Contents: Read-only** (nothing else).
   - Where can this app be installed: **Only this account**.
   - Generate a **private key** (downloads a `.pem`).
2. **Install the App** on the `hydn-co` org, scoped to **All repositories** (or at
   minimum: `substrate` + every repo that consumes a private module).
3. **Store org-level Actions secrets** (Org → Settings → Secrets and variables →
   Actions → New organization secret), visible to all private repos:
   - `MESH_MODULES_APP_ID` = the App's numeric App ID.
   - `MESH_MODULES_APP_KEY` = the full contents of the `.pem` private key.

The installation token is auto-rotating (≈1h), centrally revocable (uninstall the
App), and auditable — no long-lived PATs or per-repo deploy keys to manage.

## CI usage (Go build / test / lint)

Add one step **after** `actions/setup-go` and **before** any `go mod download`,
`go build`, `go test`, or `golangci-lint` step (the linter compiles too):

```yaml
- uses: actions/setup-go@v6
  with: { go-version: "1.25.6" }

- uses: hydn-co/build-tools/.github/actions/setup-go-private@main
  with:
    app-id: ${{ secrets.MESH_MODULES_APP_ID }}
    private-key: ${{ secrets.MESH_MODULES_APP_KEY }}

- run: go mod download
```

## Docker builds (BuildKit secret, never a build-arg)

`setup-go-private` exports the token as `GH_MODULES_TOKEN`. Forward it to the
image build via `build-app`'s existing `build-secrets` input:

```yaml
- uses: hydn-co/build-tools/.github/actions/setup-go-private@main
  with:
    app-id: ${{ secrets.MESH_MODULES_APP_ID }}
    private-key: ${{ secrets.MESH_MODULES_APP_KEY }}

- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: portald
    arch: amd64
    semver: ${{ inputs.semver }}
    registry: ghcr.io
    org: hydn-co
    build-secrets: id=ghtoken,env=GH_MODULES_TOKEN
```

Dockerfile (in the `go mod download` stage; the builder stage needs `git`):

```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=secret,id=ghtoken \
    sh -c 'if [ -f /run/secrets/ghtoken ]; then \
             git config --global url."https://x-access-token:$(cat /run/secrets/ghtoken)@github.com/hydn-co/".insteadOf "https://github.com/hydn-co/"; \
           fi; \
           export GOPRIVATE=github.com/hydn-co/*; \
           GOMODCACHE=/go/pkg/mod go mod download'
```

## Local dev

No action needed — org members already have SSH access. Ensure:

```bash
go env -w GOPRIVATE=github.com/hydn-co/*
git config --global url."git@github.com:hydn-co/".insteadOf "https://github.com/hydn-co/"
```

(Installed by the mesh-utilities workspace bootstrap.)
