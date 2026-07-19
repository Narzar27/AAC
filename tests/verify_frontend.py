"""Executable behavior contract for the Module 3 frontend.

Drives the real board in headless Chromium against the real backend.
Prerequisites (started by the runner, see docs/behavior-contract.md):
  - backend:  uvicorn app.main:app --port 8000   (fresh in-memory storage)
  - frontend: python -m http.server 5500 --directory frontend

Run with: python -m tests.verify_frontend
Every line must print PASS. Not collected by pytest (verify_ prefix).

Drag-and-drop is exercised by dispatching real DragEvents with a DataTransfer
inside the page, which drives the same handlers as a user drag.
"""

import sys

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5500"

results: list[bool] = []


def check(name: str, passed: bool) -> None:
    results.append(passed)
    print(f"{'PASS' if passed else 'FAIL'}: {name}")


def drag(page, task_id: int, to_status: str) -> None:
    page.evaluate(
        """(args) => {
            const card = document.querySelector(`.card[data-task-id="${args.taskId}"]`);
            const column = document.querySelector(`.column[data-status="${args.toStatus}"]`);
            const dt = new DataTransfer();
            card.dispatchEvent(new DragEvent('dragstart', {bubbles: true, dataTransfer: dt}));
            column.dispatchEvent(new DragEvent('dragover', {bubbles: true, cancelable: true, dataTransfer: dt}));
            column.dispatchEvent(new DragEvent('drop', {bubbles: true, cancelable: true, dataTransfer: dt}));
            card.dispatchEvent(new DragEvent('dragend', {bubbles: true}));
        }""",
        {"taskId": str(task_id), "toStatus": to_status},
    )


def create_task_via_modal(page, title: str, priority: str) -> None:
    page.click("#new-task-btn")
    page.fill("#field-title", title)
    page.select_option("#field-priority", priority)
    page.click("#modal-save-btn")
    page.wait_for_selector("#modal-overlay", state="hidden")


def column_titles(page, status: str) -> list[str]:
    return page.eval_on_selector_all(
        f'.column[data-status="{status}"] .card-title',
        "els => els.map(e => e.textContent)",
    )


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        requests_log: list[tuple[str, str]] = []
        page.on("request", lambda r: requests_log.append((r.method, r.url)))

        def patch_count() -> int:
            return sum(1 for method, _ in requests_log if method == "PATCH")

        def post_count() -> int:
            return sum(1 for method, _ in requests_log if method == "POST")

        # --- Contract 3: loading state (park the /tasks route, then release) --
        pending = []
        page.route("**/tasks", lambda route: pending.append(route))
        page.goto(FRONTEND)
        page.wait_for_selector("#board-message:not([hidden])")
        loading_text = page.text_content("#board-message")
        check("Loading state appears while fetch is pending", "Loading" in loading_text)
        for route in pending:
            route.continue_()
        page.unroute("**/tasks")
        page.wait_for_selector("#board-message", state="hidden")

        # --- Contract 1 + 4: three columns render, empty placeholders ---------
        headers = page.eval_on_selector_all(
            ".column-header h2", "els => els.map(e => e.textContent)"
        )
        check("Three columns render (To Do, In Progress, Done)",
              headers == ["To Do", "In Progress", "Done"])
        empties = page.query_selector_all(".column-empty")
        check("Empty state placeholder shown per empty column", len(empties) == 3)

        # --- Modal flow 1: empty title blocks the request ---------------------
        before_posts = post_count()
        page.click("#new-task-btn")
        page.fill("#field-title", "   ")
        page.click("#modal-save-btn")
        error_visible = page.is_visible("#error-title")
        modal_open = page.is_visible("#modal-overlay")
        check("Whitespace-only title: error shown, modal stays open, no request",
              error_visible and modal_open and post_count() == before_posts)
        page.keyboard.press("Escape")
        page.wait_for_selector("#modal-overlay", state="hidden")

        # --- Modal flow 2 + contract 2: create tasks, priority sorting --------
        create_task_via_modal(page, "High task", "High")      # id 1
        create_task_via_modal(page, "Medium task", "Medium")  # id 2
        create_task_via_modal(page, "Low task", "Low")        # id 3
        page.wait_for_selector('.column[data-status="ToDo"] .card')
        check("Created tasks appear in To Do sorted High -> Medium -> Low",
              column_titles(page, "ToDo") == ["High task", "Medium task", "Low task"])

        # --- Modal flow 3: edit reorders within the column ---------------------
        page.click('.card[data-task-id="3"] .btn-icon')
        page.wait_for_selector("#modal-overlay:not([hidden])")
        prefilled = page.input_value("#field-title")
        check("Edit modal prefills current task values", prefilled == "Low task")
        page.select_option("#field-priority", "High")
        page.click("#modal-save-btn")
        page.wait_for_selector("#modal-overlay", state="hidden")
        page.wait_for_function(
            """() => document.querySelectorAll('.column[data-status="ToDo"] .card-title')[1]?.textContent === 'Low task'"""
        )
        check("Edited priority reorders card (High ties broken by lower id)",
              column_titles(page, "ToDo") == ["High task", "Low task", "Medium task"])

        # --- Contract 6: valid drag persists through PATCH ---------------------
        before = patch_count()
        drag(page, 2, "InProgress")
        page.wait_for_selector('.column[data-status="InProgress"] .card[data-task-id="2"]')
        check("Valid drag moves card and sends PATCH", patch_count() == before + 1)

        # --- Contract 8: same-column drop sends no PATCH -----------------------
        before = patch_count()
        drag(page, 1, "ToDo")
        page.wait_for_timeout(400)
        check("Same-column drop sends no PATCH request", patch_count() == before)

        # --- Contract 7: rejected drag reverts and shows the server message ----
        drag(page, 2, "Done")  # InProgress -> Done, valid
        page.wait_for_selector('.column[data-status="Done"] .card[data-task-id="2"]')
        drag(page, 2, "ToDo")  # Done -> ToDo, invalid: 422
        page.wait_for_selector("#board-message.is-error:not([hidden])")
        message = page.text_content("#board-message")
        page.wait_for_selector('.column[data-status="Done"] .card[data-task-id="2"]')
        check("Rejected drag shows server message and card stays in Done",
              "Invalid status transition" in message)

        # --- Modal flow 4: server 422 keeps modal open with message ------------
        page.click('.card[data-task-id="2"] .btn-icon')
        page.wait_for_selector("#modal-overlay:not([hidden])")
        page.select_option("#field-status", "ToDo")
        page.click("#modal-save-btn")
        page.wait_for_selector("#error-server:not([hidden])")
        server_msg = page.text_content("#error-server")
        check("Modal stays open on 422 and shows the server message",
              page.is_visible("#modal-overlay") and "Invalid status transition" in server_msg)

        # --- Modal flow 5: all four dismissal paths -----------------------------
        page.keyboard.press("Escape")
        page.wait_for_selector("#modal-overlay", state="hidden")
        escape_closes = True

        page.click("#new-task-btn")
        page.click("#modal-cancel-btn")
        cancel_closes = page.is_hidden("#modal-overlay")

        page.click("#new-task-btn")
        page.click("#modal-close-btn")
        x_closes = page.is_hidden("#modal-overlay")

        page.click("#new-task-btn")
        page.click("#modal-overlay", position={"x": 5, "y": 5})
        overlay_closes = page.is_hidden("#modal-overlay")

        # Stale-state check: reopen after the 422 above; errors must be cleared.
        page.click("#new-task-btn")
        stale_cleared = page.is_hidden("#error-server") and page.input_value("#field-title") == ""
        page.keyboard.press("Escape")

        check("Escape, Cancel, X, and overlay click all dismiss the modal",
              escape_closes and cancel_closes and x_closes and overlay_closes)
        check("Reopened modal has no stale values or errors", stale_cleared)

        # --- Contract 5: error state when the backend is unreachable ------------
        page.route("**/tasks", lambda route: route.abort())
        page.reload()
        page.wait_for_selector("#board-message.is-error:not([hidden])")
        error_text = page.text_content("#board-message")
        check("Error state appears when the fetch fails", "Could not load tasks" in error_text)
        page.unroute("**/tasks")

        browser.close()

    if all(results):
        print(f"All {len(results)} contract checks passed.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
