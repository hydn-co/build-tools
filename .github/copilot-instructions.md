# GitHub Copilot Instructions (Clear Version)

## Purpose

This document tells Copilot (and contributors) how to generate **idiomatic Go code** and follow the architecture of this SaaS platform.

---

## Architecture

* **Service Manager**: central lifecycle (`internal/servicemanager/`)
* **Global Services**: system-wide (`internal/business/global/services/`)
* **Scoped Services**: tenant-specific (`internal/business/scoped/services/`)
* **Boundaries**

  * Domain: core business (`.../scoped/services/domain/`)
  * Catalog: read models/data intelligence (`.../scoped/services/catalog/`)
  * Shared: common infra (`.../scoped/services/shared/`)
* **Factories**

  ```go
  type GlobalServiceFactory func(messaging.MessageBus, streamkit.Client) lifecycle.Service
  type ScopedServiceFactory func(messaging.MessageBus, streamkit.Client, uuid.UUID) lifecycle.Service
  ```

---

## Service Patterns

* **Command Service** → handle writes, emit events
* **Query Service** → consume events, build read models
* **Workflow Service** → react to events across domains (choreography)
* **Unified Service** → simple domain = one `service.go`
* **Base Types** → always embed `shared.ScopedServiceBase` or `shared.GlobalServiceBase`

### Templates

```go
// Command Service
func NewTeamCommandService(bus messaging.MessageBus, stream streamkit.Client, tid uuid.UUID) lifecycle.Service {
  s := &TeamCommandService{ScopedServiceBase: shared.NewScopedServiceBase(bus, stream, tid)}
  processors.RegisterRequestHandler(s, requests.AddTeamRoute(tid), s.addTeam)
  return s
}

// Query Service
func NewTeamQueryService(bus messaging.MessageBus, stream streamkit.Client, tid uuid.UUID) lifecycle.Service {
  s := &TeamQueryService{
    ScopedServiceBase: shared.NewScopedServiceBase(bus, stream, tid),
    teams: map[uuid.UUID]*models.TeamModel{},
  }
  processors.RegisterRequestHandler(s, requests.ListTeamsRoute(tid), s.listTeams)
  processors.RegisterStreamHandler(s, areas.AreaTeams, s.teamAdded)
  return s
}

// Workflow Service (Choreography)
func NewNotificationWorkflowService(bus messaging.MessageBus, stream streamkit.Client, tid uuid.UUID) lifecycle.Service {
  s := &NotificationWorkflowService{ScopedServiceBase: shared.NewScopedServiceBase(bus, stream, tid)}
  processors.RegisterStreamHandler(s, areas.AreaTeams, s.teamMemberAdded)
  processors.RegisterStreamHandler(s, areas.AreaBoards, s.boardCreated)
  return s
}
```

---

## Event Choreography (Preferred)

* React to events; do **not** call other services directly
* Handlers must be **idempotent** and **fast**
* Return `nil` for handled/ignored events (never block streams)

---

## Multi-Tenancy

* Every scoped service must take a `tenantID (uuid.UUID)`
* Bus and stream initialized per tenant
* Global services handle cross-tenant work

---

## Coding Guidelines (Go)

* Format with `gofmt`, follow Go naming conventions
* Keep functions small and focused
* Always pass `context.Context` in public APIs
* Prefer `errors.Is` / `errors.As`
* Use `slog` for logging with context (`tenantID`, requestID)
* Return early (avoid deep nesting)

---

## Testing Guidelines

* Use Go `testing` + `testify`
* Structure: Arrange / Act / Assert
* Each test should test one thing
* Prefer table-driven tests
* Name tests in behavioral style:

  ```go
  func TestShouldReturnErrorWhenUserIsInvalid(t *testing.T) {}
  func TestShouldStoreResultGivenValidInput(t *testing.T) {}
  ```

---

## Property Naming Conventions

* **Go**: Struct = PascalCase, JSON = snake_case
* **TypeScript**

  * API interfaces = `snake_case`
  * Internal app types = `camelCase`
* **Dates**

  * `{PastTense}On` = date only (`createdOn` = YYYY-MM-DD)
  * `{PastTense}At` = date+time (`createdAt` = YYYY-MM-DDTHH:MM:SSZ)

Example:

```go
type Team struct {
  CreatedAt time.Time `json:"created_at"`
}
```

```ts
// API
type TeamDto = { created_at: string }
// App
type Team = { createdAt: string }
```

---

## CQRS / Event Sourcing Rules

* Commands → aggregates → domain events
* Queries → consume events → read models
* Workflows → react to cross-domain events
* All handlers → idempotent, non-blocking

---

## Service Registration

* Register in `internal/servicemanager/boot.go`
* Use correct factory: Global vs Scoped

---

## Development Commands

```bash
# Build
go build ./cmd/meshd ./cmd/portald ./cmd/brokerd ./cmd/streamd ./cmd/workerd ./cmd/clientd

# Test
go test ./...

# Frontend
cd ui/portal && npm i && npm run dev && npm run build && npm test && npm run lint && npm run format
```

---

## Copilot: Do / Don’t

**Do**

* Follow the service templates
* Use choreography (events > direct calls)
* Always include `context.Context` and `slog`
* Follow naming conventions (Go/TS examples above)
* Write table-driven tests

**Don’t**

* Don’t call services directly (no orchestration)
* Don’t skip factories or base services
* Don’t block streams with long tasks (emit events instead)
* Don’t mix domain and catalog logic

---

## Docs Map

* `docs/architecture/scoped-services.md` → patterns, history
* `docs/domain/services.md` → domain details
* `docs/domain/conventions.md` → naming conventions (authoritative)
