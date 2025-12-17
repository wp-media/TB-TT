## Project Templates

### Pull Request Template

When creating pull requests, use this structure:

```markdown
## Description

Fixes #issuenumber

## Type of change

- [ ] New feature (non-breaking change which adds functionality).
- [ ] Bug fix (non-breaking change which fixes an issue).
- [x] Enhancement (non-breaking change which improves an existing functionality).
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as before).
- [ ] Sub-task of #(issue number)
- [ ] Chore
- [ ] Release

## Detailed scenario

### What was tested

To be tested.

### How to test

To be tested.

### Affected Features & Quality Assurance Scope

## Technical description

### Documentation

Add here what documentation was added. But documentation should be added in the repo itself (/docs).

### New dependencies

Add here dependencies for this PR.

### Risks

Add here risks involving this PR

## Mandatory Checklist

### Code validation

- [ ] I validated all the Acceptance Criteria. If possible, provide screenshots or videos.
- [ ] I triggered all changed lines of code at least once without new errors/warnings/notices.
- [ ] I implemented built-in tests to cover the new/changed code.

### Code style

- [ ] I wrote a self-explanatory code about what it does.
- [ ] I protected entry points against unexpected inputs.
- [ ] I did not introduce unnecessary complexity.
- [ ] Output messages (errors, notices, logs) are explicit enough for users to understand the issue and are actionnable.

### Unticked items justification

Add here justification for why you didn't check everything above.

### Additional Checks

- [ ] In the case of complex code, I wrote comments to explain it.
- [ ] When possible, I prepared ways to observe the implemented system (logs, data, etc.).
- [ ] I added error handling logic when using functions that could throw errors (HTTP/API request, filesystem, etc.)
```

### Bug Grooming Template

When grooming bugs, use this structure:

```markdown
**Reproduce the problem**

1. Do this
2. Then

**Identify the root cause**
The issue is that …

**Scope a solution**
To solve the issue, we must …

**Development steps:**

- [ ] Add DB column
- [ ] Create new endpoint
- [ ] Implement business logic

**How will this be validated?**
Consider manual test scenarios and possible automations. Will a specific setup be needed?

**Grooming confidence level**
Are you sure the proposed solution will work? Have you tested it? Do you foresee any risks or unknowns?

**Can be peer-coded:** Yes/No

**Is a refactor needed in that part of the codebase?**
Yes, the data layer could be re-written to be more generic, easing future updates. This would make the effort size XS/S/M/L/XL.

**Effort estimation:** XS/S/M/L/XL
```

### User Story Grooming Template

When grooming user stories, use this structure:

```markdown
**Scope a solution**
To implement this feature, we must …

**Development steps**

- [ ] Add DB column
- [ ] Create new endpoint
- [ ] Implement business logic

**How will this be validated?**
Consider manual test scenarios and possible automations. Will a specific setup be needed?

**Grooming confidence level:**
Are you sure the proposed solution will work? Have you tested it? Do you foresee any risks or unknowns?

**Can be peer-coded:** Yes/No

**Is a refactor needed in that part of the codebase?**
Yes, the data layer could be re-written to be more generic, easing future updates. This would make the effort size XS/S/M/L/XL.

**Effort estimation:** XS/S/M/L/XL
```

Remember: This is an internal tool, so prioritize reliability and maintainability over public-facing features.
