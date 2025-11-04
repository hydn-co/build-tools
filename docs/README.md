# Build Tools Documentation

Welcome to the mesh ecosystem build tools documentation! This directory contains comprehensive guides for using and contributing to our centralized GitHub Actions.

## 📚 Documentation Index

### Getting Started

- [README](../README.md) - Main overview and quick start guide

### Features & Usage

- [Advanced Features](./advanced-features.md) - Comprehensive outputs, caching, and advanced workflows
- [Error Handling](./error-handling.md) - Validation, resilience, and troubleshooting
- [Security](./security.md) - Best practices for secure deployments and secret handling

## 🚀 Quick Links

### Available Actions

- **Container Build Actions**
  - `.github/actions/build-app` - Single-architecture container builds
  - `.github/actions/build-manifest` - Multi-architecture manifest creation
- **Deployment Actions**
  - `.github/actions/deploy-bicep` - Azure Bicep template deployment
  - `.github/actions/deploy-image` - Container image deployment
- **Utility Actions**
  - `.github/actions/create-tag` - Git tag creation and management
  - `.github/actions/prune-packages` - Container registry cleanup
  - `.github/actions/prune-tags` - Git tag cleanup

## 📖 How to Use This Documentation

1. **New to build-tools?** Start with the [main README](../README.md)
2. **Looking for specific features?** Check [Advanced Features](./advanced-features.md)
3. **Troubleshooting issues?** See [Error Handling](./error-handling.md)
4. **Security concerns?** Review [Security Best Practices](./security.md)

## 🤝 Contributing

When adding new actions or features, please update the relevant documentation:

- Add new actions to this index
- Document error handling patterns in `error-handling.md`
- Include security considerations in `security.md`
- Add advanced usage examples to `advanced-features.md`

## 📞 Support

For questions or issues:

1. Check the relevant documentation section
2. Review action-specific error messages
3. Open an issue in the repository
