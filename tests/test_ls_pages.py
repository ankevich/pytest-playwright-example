import time
from playwright.sync_api import Page, expect
import re
import pytest
from loguru import logger

BASE_URL = "https://www.lightspeedhq.com/"


@pytest.fixture(scope="function", autouse=True)
def to_intro_page(page: Page):
    """
    This fixture will go to the base URL after each test.
    If required, inside the test use page.goto
    """
    logger.info(f"Going to the base URL {BASE_URL}")
    # Go to the starting url before each test.
    page.goto(BASE_URL)
    yield


def test_page_title(page: Page):
    """
    Simple test to verify the page title
    """
    expect(page).to_have_title(re.compile("Lightspeed"))


def close_popup_if_exists(page: Page):
    """
    This function will close the popup if it exists
    """
    popup_locator = page.get_by_role("button", name="Close")
    time.sleep(5)  # wait for the popup to appear

    if popup_locator.is_visible():
        logger.info("Popup found, closing it")
        popup_locator.click(timeout=10000)
    else:
        logger.info("Popup not found")


def test_watch_demo(page: Page):
    """
    This test goes to the Watch demo page and verifies that boxes are visible
    """
    # close the advertisement popup
    close_popup_if_exists(page)
    # click the watch demo link
    page.get_by_role("link", name="Watch a demo").first.click()
    test_values = ["Retail", "Restaurant", "Golf"]
    for test_value in test_values:
        logger.info(f"Checking for {test_value}")
        test_box = page.locator("form").get_by_role("button", name=test_value)
        expect(test_box).not_to_be_empty()
        expect(test_box).to_be_visible()
        expect(test_box).to_have_text(test_value, use_inner_text=True)


def test_login_page(page: Page):
    """
    This test verifies that after clicking the login, we see the correct boxes
    """
    # close the advertisement popup
    close_popup_if_exists(page)

    page.get_by_role("menuitem", name="Login").click()

    page.get_by_text("Retail POS (X-Series) formerly Vend").click()
    page.locator("p").filter(has_text="Restaurant POS (L-Series)").click()
    page.locator("p").filter(has_text="eCommerce (E-Series)").click()

    test_values = [
        "Retail POS (X-Series) formerly Vend",
        "Restaurant POS (L-Series)",
        "eCommerce (E-Series)",
    ]
    for test_value in test_values:
        logger.info(f"Checking for {test_value}")
        test_box = page.locator("p").filter(has_text=test_value)
        expect(test_box).not_to_be_empty()
        expect(test_box).to_be_visible()
        expect(test_box).to_have_text(test_value, use_inner_text=True)


@pytest.mark.parametrize(
    ["email", "case"],
    [("test@example.com", "positive"), ("testNotAnEmail", "negative")],
)
def test_email_input(page: Page, email: str, case: str):
    """
    Example of a parametrized test that checks the email input
    """
    page.goto("https://www.lightspeedhq.com/partners/partner-application/")
    email_form = page.query_selector("#leadform-1_email")
    email_form.fill(email)
    page.mouse.click(1, 1)  # click away from the form to trigger the input validation
    error_message = page.get_by_text("Please enter a valid email address")

    if case == "negative":
        expect(error_message).to_be_visible()
    else:
        expect(error_message).to_be_hidden()