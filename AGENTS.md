# AGENTS.md

## Purpose
- This file defines repository-specific guidance for Tkinter example refactoring and new example creation.
- Apply these rules when working on Tkinter demo files in this repository unless the user explicitly asks for a different style.

## Tkinter Refactoring Rules
- Prefer class-based structure with `class App(tk.Tk)` for runnable GUI examples.
- Avoid leaving UI construction or event binding in module-level executable code.
- Keep startup logic in `main()` and guard it with `if __name__ == "__main__": main()`.
- Split UI creation into focused internal methods such as `_build_menu()`, `_build_body()`, `_build_treeview()`, and `_build_statusbar()`.
- Move callbacks and event handlers into instance methods instead of standalone functions when refactoring.
- Store widgets and state on `self`, for example `self.treeview`, `self.status_var`, and `self.style`.
- Keep utility behavior such as window centering in small helper methods when useful, for example `center_window()`.

## Style Baseline
- Use `Chapter00/c003_Menubutton.py` as the primary local style reference for Tkinter refactoring.
- Match its overall structure, spacing, naming style, and method organization where reasonable.
- Prefer clear method names over generic names. Use `_build_*` for UI sections and verb-based names for event handlers.
- Keep imports minimal and grouped clearly.
- Maintain readable blank-line spacing between class methods and top-level functions.

## Legacy Code Preservation
- When the user asks to preserve existing code during refactoring, do not delete it immediately.
- Keep old code in a clearly marked `# Legacy code` section as commented code.
- Place the legacy block near the end of the file unless keeping it adjacent to the refactored block makes comparison easier.
- If the user does not ask to preserve old code, normal cleanup is allowed.

## Scope Notes
- These rules are intended for educational example files in this repository.
- If an existing chapter file already follows a different local pattern and the user asks to preserve that pattern, follow the chapter-local pattern instead.
- If a task is not about Tkinter example structure, use normal engineering judgment rather than forcing these rules.
