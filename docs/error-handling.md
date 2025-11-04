# Error Handling & Resilience

This document describes the error handling and validation improvements made to all composite actions.

## Phase 2 Improvements

### Validation & Pre-Flight Checks

All actions now validate inputs before attempting operations:

#### `build-app`

- ✅ **Architecture validation**: Ensures `arch` is either `amd64` or `arm64`
- ✅ **Semver format validation**: Verifies version follows `vX.Y.Z` pattern
- ✅ **Dockerfile existence check**: Confirms Dockerfile exists before building
- ✅ **Build failure detection**: Captures Docker build failures with context
- ✅ **Push failure detection**: Captures registry push failures with helpful messages

#### `build-manifest`

- ✅ **Semver format validation**: Verifies version follows `vX.Y.Z` pattern
- ✅ **Architecture image verification**: Checks both amd64 and arm64 images exist
- ✅ **Manifest creation failure handling**: Provides detailed error context
- ✅ **Clear missing image reporting**: Lists exactly which architectures are missing

#### `deploy-bicep`

- ✅ **Semver format validation**: Verifies version follows `vX.Y.Z` pattern
- ✅ **Boolean validation**: Ensures `applyCerts` is `true` or `false`
- ✅ **Azure CLI authentication check**: Verifies user is logged in before deployment
- ✅ **Template file existence**: Confirms Bicep template exists
- ✅ **Parameters file existence**: Confirms environment-specific parameters exist
- ✅ **Deployment failure handling**: Provides direct link to Azure Portal for errors
- ✅ **Subscription display**: Shows which Azure subscription is being used

#### `deploy-image`

- ✅ **Semver format validation**: Verifies version follows `vX.Y.Z` pattern
- ✅ **Required credentials check**: Ensures GHCR username and token are provided
- ✅ **Azure CLI authentication check**: Verifies user is logged in
- ✅ **ACR existence verification**: Confirms target ACR exists and is accessible
- ✅ **Import failure handling**: Provides troubleshooting guidance for common issues
- ✅ **Network/permission diagnostics**: Suggests verification commands

## Error Message Structure

All error messages follow a consistent pattern:

```
❌ ERROR: <Brief description>
   <Context details>
   <Resource information>

   <Troubleshooting guidance>
   <Verification commands>
```

### Example Error Output

```bash
❌ ERROR: Bicep deployment failed
   Deployment name: mesh-auth-dev1
   Location: eastus
   Template: ./.deploy/bicep/main.bicep
   Parameters: ./.deploy/bicep/parameters/dev1.bicepparam

   Check the Azure Portal for detailed error messages:
   https://portal.azure.com/#view/HubsExtension/DeploymentDetailsBlade/...
```

## Benefits

1. **Fail Fast**: Validates inputs before expensive operations
2. **Clear Diagnostics**: Provides exact context when failures occur
3. **Actionable Guidance**: Suggests specific commands to verify or fix issues
4. **Resource Information**: Shows exactly what was being attempted
5. **Portal Integration**: Provides direct links to Azure Portal for cloud errors

## Testing Error Scenarios

To verify error handling works correctly:

### Invalid Architecture

```yaml
- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    arch: x86 # ❌ Will fail with clear message
```

### Missing Dockerfile

```yaml
- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: nonexistent # ❌ Will list available cmd/ directories
```

### Invalid Semver

```yaml
- uses: hydn-co/build-tools/.github/actions/deploy-bicep@main
  with:
    semver: 1.2.3 # ❌ Will fail (missing 'v' prefix)
```

### Missing ACR

```yaml
- uses: hydn-co/build-tools/.github/actions/deploy-image@main
  with:
    acr_name: nonexistent # ❌ Will list available ACRs
```

## Backward Compatibility

All enhancements are **100% backward compatible**:

- No changes to action inputs or outputs
- Additional validations only trigger on error conditions
- Success path behavior unchanged
- Error messages enhanced but exit codes remain consistent
