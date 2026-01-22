---
name: audit
description: Full codebase audit running all validation agents. Use for comprehensive quality/security/compliance checks before releases or after major changes.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: [full | quick | security | quality | compliance]
---

# Audit Skill - Full Codebase Validation

Runs multiple validation agents in sequence for comprehensive codebase review.

## Invocation

```
/audit              # Full audit (all checks)
/audit quick        # Quick audit (essential checks only)
/audit security     # Security-focused audit
/audit quality      # Code quality audit
/audit compliance   # CLAUDE.md and standards compliance
```

---

## Audit Levels

### Full Audit (`/audit` or `/audit full`)

Runs ALL validation agents:

```
1. claude-md-compliance-checker  → CLAUDE.md rule compliance
2. code-quality-pragmatist       → Over-engineering check
3. code-reviewer                 → Code quality/security
4. jenny                         → Spec vs implementation match
5. karen                         → Reality check on completions
6. task-completion-validator     → Verify claimed completions
7. security-auditor              → Security assessment
8. architect-reviewer            → Architecture validation
```

**When to use:** Before releases, after major refactors, quarterly reviews

### Quick Audit (`/audit quick`)

Essential checks only:

```
1. claude-md-compliance-checker  → CLAUDE.md compliance
2. code-quality-pragmatist       → Over-engineering check
3. karen                         → Reality check
```

**When to use:** After completing features, before PRs

### Security Audit (`/audit security`)

```
1. security-auditor              → Full security assessment
2. code-reviewer (security mode) → Security vulnerabilities
3. penetration-tester            → Security testing
```

**When to use:** Before production deployments, after auth changes

### Quality Audit (`/audit quality`)

```
1. code-reviewer                 → Code quality
2. code-quality-pragmatist       → Over-engineering
3. architect-reviewer            → Architecture decisions
```

**When to use:** After refactors, code reviews

### Compliance Audit (`/audit compliance`)

```
1. claude-md-compliance-checker  → CLAUDE.md rules
2. jenny                         → Spec compliance
3. compliance-auditor            → Standards compliance
```

**When to use:** Before milestone completion

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    FULL AUDIT FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. COMPLIANCE CHECK                                        │
│     └── claude-md-compliance-checker                        │
│         • Goal counting rules                               │
│         • Vectorization rules                               │
│         • Key formatting                                    │
│                                                             │
│  2. QUALITY CHECK                                           │
│     ├── code-quality-pragmatist                             │
│     │   • Over-engineering detection                        │
│     │   • Unnecessary complexity                            │
│     └── code-reviewer                                       │
│         • Code quality                                      │
│         • Best practices                                    │
│                                                             │
│  3. IMPLEMENTATION CHECK                                    │
│     ├── jenny                                               │
│     │   • Spec vs implementation                            │
│     ├── karen                                               │
│     │   • Reality check on completions                      │
│     └── task-completion-validator                           │
│         • Verify claimed work                               │
│                                                             │
│  4. SECURITY CHECK                                          │
│     └── security-auditor                                    │
│         • Vulnerabilities                                   │
│         • Auth/access control                               │
│                                                             │
│  5. ARCHITECTURE CHECK                                      │
│     └── architect-reviewer                                  │
│         • Design decisions                                  │
│         • Scalability                                       │
│                                                             │
│  6. REPORT                                                  │
│     └── Generate audit report with findings                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Output

Each audit generates a report with:

```markdown
# Audit Report - YYYY-MM-DD

## Summary
- Total issues: N
- Critical: N
- Warnings: N
- Passed: N

## Findings by Category

### Compliance
- [list findings]

### Quality
- [list findings]

### Security
- [list findings]

### Architecture
- [list findings]

## Recommended Actions
1. [priority action]
2. [priority action]
...
```

---

## Integration

After audit, consider:
- `/pm reorg` - If issues found need tracking
- Create GitHub issues for critical findings
- Update docs if compliance gaps found

---

## Notes

- Full audit can take 5-10 minutes
- Use `/audit quick` for routine checks
- Critical findings should block releases
