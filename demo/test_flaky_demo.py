import pathlib

PAGE_PATH = pathlib.Path(__file__).parent / "flaky_page.html"
PAGE_URL = f"file://{PAGE_PATH}"


def test_reveal_waits_properly(page):
    """Waits for the element itself, so it's stable regardless of the random delay."""
    page.goto(PAGE_URL)
    page.click("#show-btn")
    page.wait_for_selector("#target", timeout=2000)
    assert page.is_visible("#target")


def test_reveal_with_a_race_condition(page):
    """Uses a fixed wait shorter than the page's random delay range.

    Sometimes the delay is under 50ms and this passes. Sometimes it isn't
    and this fails. That's the point: this is what flaky_detector.py is
    built to catch.
    """
    page.goto(PAGE_URL)
    page.click("#show-btn")
    page.wait_for_timeout(50)
    assert page.is_visible("#target")
