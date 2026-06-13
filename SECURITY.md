# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the Crypto Smart Money AI Agent, please report it responsibly:

1. **DO NOT** open a public issue on GitHub
2. **DO** email security details to the maintainers
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and work with you to resolve the issue.

## Security Considerations

### API Keys & Credentials
- ✅ Always use environment variables (.env)
- ❌ Never commit .env files to Git
- ❌ Never share API keys publicly
- ✅ Rotate keys regularly

### Database Security
- ✅ Use strong passwords for PostgreSQL
- ✅ Enable authentication on all databases
- ❌ Never expose database URLs publicly
- ✅ Use read-only accounts where appropriate

### VPS Security
- ✅ Keep system updated
- ✅ Use SSH keys (not passwords)
- ✅ Enable firewall
- ✅ Use HTTPS with SSL certificates
- ❌ Don't allow root login via SSH
- ✓ Use fail2ban or similar

### Telegram Bot Security
- ✅ Keep bot token secret
- ❌ Don't expose token in logs
- ✅ Verify message authenticity
- ✅ Rate limit API calls

### Code Security
- ✅ Use parameterized queries
- ✅ Validate all inputs
- ✅ Handle errors safely (don't expose internals)
- ✅ Use type hints
- ✅ Run security scanners

## Dependencies Security

We use several third-party packages. Security recommendations:

1. Keep dependencies updated:
   ```bash
   pip install --upgrade pip
   pip list --outdated
   ```

2. Enable Dependabot:
   - GitHub automatically scans for vulnerabilities
   - Check "Dependabot alerts" in repository settings

3. Review security advisories:
   - https://github.com/advisories
   - https://pyup.io/

## Deployment Security

### Docker
- Use official base images
- Don't run as root
- Scan images for vulnerabilities
- Keep Docker updated

### Environment Variables
- Use .env files (never commit them)
- Use strong, random values
- Rotate credentials regularly
- Never log sensitive data

## Responsible Disclosure

If you find a security issue:
1. Report privately to maintainers
2. Allow time for patch development (7-30 days)
3. Don't share details publicly until patched
4. Credit the reporter in release notes (optional)

## Security Updates

Security patches will be released as soon as possible.
- Critical vulnerabilities: same day if possible
- High severity: within 7 days
- Medium/Low: next release

## Best Practices

### For Users
- Keep dependencies updated
- Use strong API keys
- Enable HTTPS on VPS
- Monitor logs for suspicious activity
- Use firewalls
- Backup databases regularly

### For Developers
- Never hardcode secrets
- Use environment variables
- Validate all inputs
- Use parameterized queries
- Handle errors gracefully
- Run security tools
- Keep dependencies updated

## Security Tools

We recommend using these tools:

- **Code Scanning**: GitHub CodeQL
- **Dependency Scanning**: Dependabot
- **SAST**: Semgrep
- **Linting**: flake8, pylint
- **Type Checking**: mypy
- **Container Scanning**: Trivy

## Questions?

For security questions (non-vulnerability):
- GitHub Discussions
- Email maintainers
- Check documentation

---

**Last Updated:** 2026-06-13
**Version:** 1.0
