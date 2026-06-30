# ultrapilot assets

This directory holds branding and diagram assets for ultrapilot.

## Recommended files to add before public release

- `logo.svg` — the ultrapilot wordmark / mark
- `diagram-loop.png` — visual of the explore → plan → build → verify → review → patch loop
- `diagram-flow.png` — decision tree for the orchestrator
- `banner.png` — README / GitHub social preview (1280×640 recommended)
- `favicon.ico`

## Diagram source

The phase diagram can be regenerated from this Mermaid source:

```mermaid
flowchart LR
    A[User] -->|/ultrapilot [task]| B[Orchestrator]
    B --> C[1. Explore]
    C --> D[2. Plan]
    D --> E{Goal clear?}
    E -->|No| F[Brainstorm]
    F --> D
    E -->|Yes| G[3. Build]
    G --> H[4. Verify]
    H --> I{All checks pass?}
    I -->|No| G
    I -->|Yes| J[5. Review]
    J --> K{Connected issues?}
    K -->|Yes| L[6. Patch]
    L --> H
    K -->|No| M[COMPLETE]
```

Add a `diagram-loop.svg` rendered from this source.
