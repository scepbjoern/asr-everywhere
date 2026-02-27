---
description: Execute an implementation plan
argument-hint: [path-to-plan]
---

# Execute: Implement from Plan

## Plan to Execute

Read plan file: `$ARGUMENTS`

## Execution Instructions

### 1. Read and Understand

- Read the ENTIRE plan carefully
- Understand all tasks and their dependencies
- Note the validation commands to run
- Review the testing strategy

### 2. Execute Tasks in Order

For EACH task in "Step by Step Tasks":

#### a. Navigate to the task
- Identify the file and action required
- Read existing related files if modifying

#### b. Implement the task
- Follow the detailed specifications exactly
- Maintain consistency with existing code patterns
- Include proper type hints and documentation
- Add structured logging where appropriate

#### c. Verify as you go
- After each file change, check syntax
- Ensure imports are correct
- Verify types are properly defined

### 3. Implement Testing Strategy

After completing implementation tasks:

- Create all test files specified in the plan
- Implement all test cases mentioned
- Follow the testing approach outlined
- Ensure tests cover edge cases

### 3.5. Extend Regression Test Suite (CRITICAL)

**IMPORTANT**: For every new feature/phase, extend the regression test suite:

- Identify core functionality that must remain stable
- Add regression tests to `tests/test_regression.py`
- Use appropriate test class: `TestConfigRegression`, `TestAudioRecorderRegression`, etc.
- Or create new regression test class for new components
- Ensure existing regression tests still pass
- Run: `python -m pytest tests/test_regression.py -v`

**Regression Test Principles:**
- Test default values and core behavior
- Test state transitions and error handling
- Test integration workflows
- Mark with `@pytest.mark.regression` decorator

### 4. Run Validation Commands

Execute ALL validation commands from the plan in order:

**Level 1 - Linting & Formatting:**
```bash
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
```

**Level 2 - Unit Tests:**
```bash
python -m pytest tests/ -v
```

**Level 3 - Regression Tests (MANDATORY):**
```bash
python -m pytest tests/test_regression.py -v
```

**Level 4 - Coverage Report:**
```bash
python -m pytest tests/ -v --cov=src/asr_everywhere --cov-report=term-missing
```

If any command fails:
- Fix the issue
- Re-run the command
- Continue only when it passes
- REGRESSION TEST FAILURES MUST BE FIXED BEFORE PROCEEDING

### 5. Final Verification

Before completing:

- ✅ All tasks from plan completed
- ✅ All tests created and passing
- ✅ **Regression tests extended and passing**
- ✅ All validation commands pass
- ✅ Code follows project conventions
- ✅ Documentation added/updated as needed
- ✅ No regressions in existing functionality

## Output Report

Provide summary:

### Completed Tasks
- List of all tasks completed
- Files created (with paths)
- Files modified (with paths)

### Tests Added
- Test files created
- Test cases implemented
- Test results

### Validation Results
```bash
# Output from each validation command
```
### User Testing Guide
Instruct the user, what he can test now to verify the implementation.

### Ready for Commit
- Confirm all changes are complete
- Confirm all validations pass
- Ready for `/commit` command

## Notes

- If you encounter issues not addressed in the plan, document them
- If you need to deviate from the plan, explain why
- If tests fail, fix implementation until they pass
- Don't skip validation steps
