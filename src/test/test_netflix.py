import pytest
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Load config ────────────────────────────────────────────────────────────────
config = configparser.ConfigParser()
config.read("src/test/resources/config.properties")

USERNAME     = config.get("DEFAULT", "username")
PASSWORD     = config.get("DEFAULT", "password")
ACCOUNT_NAME = config.get("DEFAULT", "account_name")


# ── Fixture: replaces @BeforeClass / @AfterClass ───────────────────────────────
@pytest.fixture(scope="module")
def driver():
    drv = webdriver.Chrome()
    drv.maximize_window()
    drv.get("https://www.netflix.com")
    yield drv
    drv.quit()                          # teardown — runs after all tests in module


@pytest.fixture(scope="module")
def wait(driver):
    return WebDriverWait(driver, 10)


# ── Helper ─────────────────────────────────────────────────────────────────────
def screenshot(driver, name="screenshot"):
    driver.save_screenshot(f"{name}.png")


# ── Tests (priority order preserved via file order + pytest-ordering) ──────────

def test_01_login(driver, wait):
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[role='button']"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, ":r0:"))).send_keys(USERNAME)
    wait.until(EC.visibility_of_element_located((By.ID, ":r3:"))).send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='button'][type='submit']"))).click()

    screenshot(driver, "login")
    assert "Netflix" in driver.title, f"Login failed — title was: {driver.title}"


def test_02_select_account(driver, wait):
    screenshot(driver, "select_account")
    profiles = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "span.profile-name")))
    for profile in profiles:
        if profile.text == ACCOUNT_NAME:
            profile.click()
            break


def test_03_search_and_play(driver, wait):
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Search']"))).click()
    search_input = wait.until(EC.visibility_of_element_located((By.ID, "searchInput")))
    search_input.send_keys("Black Clover")
    search_input.send_keys(Keys.ENTER)
    screenshot(driver, "search")


def test_04_add_to_list(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a[aria-label='Black Clover'] img.boxart-image")
    )).click()
    screenshot(driver, "add_to_list")
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.buttonControls--container button[aria-label='My List']")
    )).click()


def test_05_play_video(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".color-primary.hasLabel.hasIcon.ltr-podnco")
    )).click()

    for _ in range(5):
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Seek Back'] div[role='presentation'] svg")
        )).click()
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Seek Forward'] div[role='presentation'] svg")
        )).click()

    screenshot(driver, "play_video")


def test_06_change_subtitles(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[aria-label='Audio & Subtitles'] div[role='presentation'] svg path")
    )).click()
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".default-ltr-cache-1lif7jb[data-uia='subtitle-item-Thai']")
    )).click()
    screenshot(driver, "subtitles")


def test_07_close_video(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[aria-label='Back to Browse'] div[role='presentation'] svg path")
    )).click()
    screenshot(driver, "close_video")


def test_08_change_episode(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[aria-label='dropdown-menu-trigger-button']")
    )).click()
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".ltr-bbkt7g[data-index='2']")
    )).click()
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='titleCard-title_index' and text()='106']")
    )).click()
    screenshot(driver, "change_episode")


def test_09_exit_screen(driver, wait):
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[aria-label='Back to Browse'] div[role='presentation'] svg")
    )).click()
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "span[title='close'] svg")
    )).click()
    screenshot(driver, "exit_screen")


def test_10_logout(driver, wait):
    dropdown = driver.find_element(By.CSS_SELECTOR, ".account-dropdown-button")
    ActionChains(driver).move_to_element(dropdown).perform()

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class='sub-menu-link ']"))).click()
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".btn.btn-logout.btn-blue.btn-large")
    )).click()

    screenshot(driver, "logout")
    assert driver.current_url == "https://www.netflix.com/in/", \
        f"Logout failed — URL was: {driver.current_url}"
