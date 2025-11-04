# Claude 3.0 Boot Sequence
**Agent Mission Control Project**

## Automatic Startup (Execute on Every Session)

When starting a new session in this project, execute these steps:

### 1. Load Identity
Read `CLAUDE.md` - Understand you are Claude 3.0 with pipeline management capabilities

### 2. Load Context
- Read `CLAUDE_3.0_VISION.md` - Complete vision and goals
- Read `ARCHITECTURE.md` - System architecture
- Read `README.md` - Current status and quick reference

### 3. Check Project Status
```bash
# Check current phase
cat README.md | grep "Current Phase"

# Check git status
git status --short

# Check if services are running
# (Backend, Frontend, Redis, Celery)
```

### 4. Load Recent Work
- Check recent commits: `git log --oneline -5`
- Check current branch
- Check for any in-progress work

### 5. Verify Environment
- SuperOptiX installed: `super --version`
- Python environment active
- Dependencies up to date

### 6. Review Current Focus
Based on phase in README.md:
- Phase 1 (Foundation): Setting up structure
- Phase 2 (SuperOptiX Integration): Building integrations
- Phase 3 (Backend API): Building FastAPI server
- Phase 4 (Frontend MVP): Building Streamlit UI
- Phase 5+ (Advanced Features): Adding capabilities

### 7. Load Playbooks
- Read `playbooks/integration_patterns.yaml` - Proven integration approaches
- Note any high-confidence patterns (>=0.9) to apply automatically

### 8. Check for Updates
- Any new research or documentation in `docs/`
- Any updates to SuperOptiX (check for new versions/features)

### 9. Ready State
Confirm ready state:
```
Claude 3.0 Ready (Agent Mission Control)

Project: Agent Pipeline Management System
Phase: [Current Phase]
Status: [Brief status]
Next: [Next major task]

Ready to work.
```

## Example Boot Output

```
Claude 3.0 Ready (Agent Mission Control)

Project: Agent Pipeline Management System
Phase: Foundation (Week 0)
Status: Structure created, git initialized
Next: Install SuperOptiX and build first integration

Loaded:
- Identity: Claude 3.0 Producer with Mission Control
- Vision: Custom pipeline management for AI agents
- Architecture: FastAPI + Streamlit + SuperOptiX backend
- Patterns: 8 integration patterns loaded

SuperOptiX: Not yet installed
Services: Not yet running
Git: Clean, on branch main

Ready to work on Phase 2: SuperOptiX Integration
```

## Quick Commands Reference

```bash
# Start development
./scripts/start_dev.sh  # (create this in Phase 3)

# Run tests
pytest tests/

# Check system status
python -m backend.health_check  # (create this in Phase 3)

# SuperOptiX commands
super --version
super agent list
super agent compile <name>
super agent evaluate <name>
super agent optimize <name>
```

## Important Reminders

1. **Visual Verification**: Use Screenpipe to verify UI changes
2. **SuperOptiX is Backend**: We build the UI, SuperOptiX is the engine
3. **Workflow-Oriented**: Organize by user workflows, not systems
4. **No Emojis in Python**: Windows encoding breaks
5. **Document Everything**: This is compound learning

## Context to Load Per Phase

**Phase 1 (Foundation)**:
- CLAUDE.md, VISION, ARCHITECTURE, README only
- Focus: Understanding project goals

**Phase 2 (SuperOptiX Integration)**:
- Add: docs/SUPEROPTIX_RESEARCH.md
- Focus: How SuperOptiX works, API, capabilities

**Phase 3 (Backend API)**:
- Add: playbooks/integration_patterns.yaml
- Focus: API design, integration patterns

**Phase 4+ (Frontend & Beyond)**:
- Add: Specific documentation as created
- Focus: Implementation details, user workflows

---

**Last Updated**: November 4, 2025
**Project Status**: Foundation Phase
