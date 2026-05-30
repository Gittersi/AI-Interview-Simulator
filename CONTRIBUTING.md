# Contributing Guide

## How to Contribute

### Setting Up Development Environment

Follow the [SETUP.md](./SETUP.md) guide for initial setup.

### Code Style

- **Python**: Follow PEP 8 using Black formatter
  ```bash
  black app/
  ```

- **TypeScript/React**: Follow ESLint rules
  ```bash
  npm run lint
  ```

### Committing Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: description of your change"
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request

### Pull Request Guidelines

- Provide clear description of changes
- Include relevant screenshots/videos for UI changes
- Ensure all tests pass
- Update documentation if needed
- Follow existing code patterns

## Areas for Contribution

### Backend
- [ ] Improve LLM integration
- [ ] Add more question datasets
- [ ] Enhance evaluation algorithms
- [ ] Add database optimization
- [ ] Implement caching layer

### Frontend
- [ ] Improve UI/UX
- [ ] Add animations
- [ ] Implement offline mode
- [ ] Add mobile responsiveness
- [ ] Create additional charts

### ML/NLP
- [ ] Improve answer evaluation
- [ ] Better confidence scoring
- [ ] Enhanced resume parsing
- [ ] New evaluation metrics

### Infrastructure
- [ ] CI/CD setup
- [ ] Deployment configs
- [ ] Monitoring/logging
- [ ] Database migration scripts

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Documentation

When adding new features:
1. Update relevant README sections
2. Add code comments for complex logic
3. Document new API endpoints
4. Include usage examples

## Questions?

Feel free to open an issue for questions or discussions.
