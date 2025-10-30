# Action Normalization & Migration Guide

## 📊 Analysis Summary

### Common Actions Identified

| Action | Instances | Identical | Variations | Status |
|--------|-----------|-----------|------------|--------|
| `build-app` | 4 | 3 | 1 (mesh-core comment only) | ✅ Normalized |
| `build-manifest` | 4 | 3 | 1 (mesh-core comment only) | ✅ Normalized |
| `deploy-bicep` | 4 | 4 | 0 | ✅ Normalized |
| `deploy-image` | 4 | 0 | 4 (minor whitespace) | ✅ Normalized |

### Hash Analysis Results

```
build-app:
  mesh-auth   : 852E6337  ─┐
  mesh-broker : 852E6337  ├─ Identical (3/4)
  mesh-stream : 852E6337  ┘
  mesh-core   : 8926E90C  ← Minor difference (example comment)

build-manifest:
  mesh-auth   : 1942E145  ─┐
  mesh-broker : 1942E145  ├─ Identical (3/4)
  mesh-stream : 1942E145  ┘
  mesh-core   : E5B2666A  ← Minor difference (example comment)

deploy-bicep:
  mesh-auth   : C82B061A  ─┐
  mesh-broker : C82B061A  ├─ Identical (4/4) ✅
  mesh-stream : C82B061A  │
  mesh-core   : C82B061A  ┘

deploy-image:
  mesh-auth   : 38CAD9B6  ─┐
  mesh-broker : 37207CAB  ├─ Whitespace differences
  mesh-stream : 38CAD9B6  │
  mesh-core   : E3568F16  ┘
```

## 🎯 Normalization Goals

1. **Eliminate Duplication**: Move from 16 action files (4 actions × 4 repos) to 4 centralized actions
2. **Improve Maintainability**: Single source of truth for all actions
3. **Enhanced Documentation**: Better descriptions, examples, and usage patterns
4. **Consistent Behavior**: Identical implementation across all projects
5. **Version Control**: Ability to pin to specific versions or use latest

## ✨ Improvements Made

### 1. Enhanced Descriptions
**Before:**
```yaml
description: "Builds and pushes a container for a given app and arch"
```

**After:**
```yaml
description: "Builds and pushes a single-architecture container image for a mesh application"
```

### 2. Better Input Documentation
**Before:**
```yaml
app:
  required: true
  description: "App to build (e.g., portald)"
```

**After:**
```yaml
app:
  description: "Application name (e.g., authd, brokerd, streamd, apigwd, workerd)"
  required: true
```

### 3. Improved Logging
**Before:**
```yaml
echo "Checking if $IMAGE:$SEMVER-$ARCH exists in registry..."
```

**After:**
```yaml
echo "📦 Checking if $IMAGE:$SEMVER-$ARCH exists in registry..."
```

### 4. Better Error Messages
**Before:**
```yaml
echo "⚠️ Missing $IMAGE:$SEMVER-$arch"
```

**After:**
```yaml
echo "⚠️  Missing $IMAGE:$SEMVER-$arch"
missing_arches+=("$arch")
# ...
echo "❌ Cannot create manifest, missing architecture(s): ${missing_arches[*]}"
```

### 5. Flexible Parameters
**deploy-bicep** now supports:
- Configurable location (default: eastus)
- Custom template path
- Custom parameters path
- Smart path resolution (auto-append environment if needed)

### 6. Output Values
**build-manifest** now returns:
```yaml
outputs:
  manifest:
    description: "Full image reference for the created manifest"
    value: ${{ steps.manifest.outputs.manifest }}
```

## 🔄 Migration Steps

### Step 1: Update Workflow to Use Centralized Actions

**Before:**
```yaml
jobs:
  build:
    steps:
      - uses: ./.github/actions/build-app
        with:
          app: authd
          arch: amd64
          semver: ${{ needs.version.outputs.semver }}
          registry: ghcr.io
          org: hydn-co
```

**After:**
```yaml
jobs:
  build:
    steps:
      - uses: hydn-co/build-tools/actions/build-app@main
        with:
          app: authd
          arch: amd64
          semver: ${{ needs.version.outputs.semver }}
          registry: ghcr.io
          org: hydn-co
```

### Step 2: Test in Development Environment

1. Create a test branch
2. Update one workflow to use centralized action
3. Trigger workflow manually or via push
4. Verify output and behavior match previous implementation

### Step 3: Roll Out to All Workflows

Update in this order:
1. **mesh-core** (newest, least critical in production)
2. **mesh-stream**
3. **mesh-broker**
4. **mesh-auth** (most critical, do last)

### Step 4: Remove Local Actions

After all workflows are updated and tested:

```powershell
# For each repository
Remove-Item -Recurse -Force .github/actions/build-app
Remove-Item -Recurse -Force .github/actions/build-manifest
Remove-Item -Recurse -Force .github/actions/deploy-bicep
Remove-Item -Recurse -Force .github/actions/deploy-image
```

## 📋 Migration Checklist

### Per Repository

- [ ] **Update containers.yml**
  - [ ] Replace `build-app` references
  - [ ] Replace `build-manifest` references
  - [ ] Test container build workflow

- [ ] **Update deploy.yml**
  - [ ] Replace `deploy-bicep` references
  - [ ] Replace `deploy-image` references
  - [ ] Test deployment workflow

- [ ] **Verify Workflows**
  - [ ] Test CI workflow (no action changes, but verify)
  - [ ] Test version workflow (no action changes)
  - [ ] Test cleanup workflow (no action changes)

- [ ] **Cleanup**
  - [ ] Remove local `.github/actions/` directory
  - [ ] Update documentation references
  - [ ] Commit and push changes

### Repositories to Update

- [ ] **mesh-auth**
  - [ ] Update workflows
  - [ ] Test all workflows
  - [ ] Remove local actions
  - [ ] Update README if needed

- [ ] **mesh-broker**
  - [ ] Update workflows
  - [ ] Test all workflows
  - [ ] Remove local actions
  - [ ] Update README if needed

- [ ] **mesh-stream**
  - [ ] Update workflows
  - [ ] Test all workflows
  - [ ] Remove local actions
  - [ ] Update README if needed

- [ ] **mesh-core**
  - [ ] Update workflows
  - [ ] Test all workflows
  - [ ] Remove local actions
  - [ ] Update README if needed

## 🎓 Best Practices

### Version Pinning

**Development:**
```yaml
uses: hydn-co/build-tools/actions/build-app@main
```

**Production (Recommended):**
```yaml
uses: hydn-co/build-tools/actions/build-app@v1
```

**Maximum Stability:**
```yaml
uses: hydn-co/build-tools/actions/build-app@v1.2.3
```

### Testing Changes

1. Always test in a feature branch first
2. Use `workflow_dispatch` to manually trigger workflows
3. Monitor workflow logs for any differences in behavior
4. Verify output artifacts (containers, deployments) match expected results

### Updating Centralized Actions

When updating actions in `build-tools/`:

1. Make changes in a feature branch
2. Test changes in at least one consumer repository
3. Create PR with clear description and examples
4. Tag new version after merge if needed
5. Update consumer repositories to use new version

## 🔍 Validation

### Before Migration

```powershell
# Check current action usage
$services = @('mesh-auth', 'mesh-broker', 'mesh-stream', 'mesh-core')
foreach ($svc in $services) {
    Write-Host "`n$svc actions:"
    Get-ChildItem "$svc\.github\actions" -Directory | Select-Object Name
}
```

### After Migration

```powershell
# Verify no local actions remain
$services = @('mesh-auth', 'mesh-broker', 'mesh-stream', 'mesh-core')
foreach ($svc in $services) {
    $actionsPath = "$svc\.github\actions"
    if (Test-Path $actionsPath) {
        Write-Host "⚠️  $svc still has local actions"
    } else {
        Write-Host "✅ $svc migrated successfully"
    }
}
```

### Workflow Test Commands

```powershell
# Test workflows in each repository
cd mesh-auth
gh workflow run containers.yml
gh workflow run deploy.yml --field environment=dev1

# Monitor workflow status
gh run list --limit 5
```

## 📈 Expected Benefits

### Immediate
- ✅ Consistent action behavior across all repositories
- ✅ Improved logging and error messages
- ✅ Better documentation in workflow files

### Short-term
- ✅ Reduced maintenance burden (update once vs. 4 times)
- ✅ Easier to add new services (copy workflow, works immediately)
- ✅ Faster bug fixes (single location to update)

### Long-term
- ✅ Ability to version actions independently
- ✅ Easier to add new features (e.g., caching, notifications)
- ✅ Foundation for more sophisticated reusable workflows

## 🚨 Rollback Plan

If issues arise after migration:

1. **Quick Fix**: Revert workflow changes in affected repository
   ```yaml
   # Change back to local action
   uses: ./.github/actions/build-app
   ```

2. **Restore Local Actions**: Copy from git history
   ```powershell
   git checkout HEAD~1 -- .github/actions/
   ```

3. **Fix Centralized Action**: Update build-tools and re-migrate

## 📚 Additional Resources

- [Creating Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Reusing Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
