from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from audio import AudioRecorder
import time
from state import in_meeting
import subprocess

CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
recorder = AudioRecorder()


chrome_options = webdriver.ChromeOptions()
user_agent = "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_experimental_option("prefs", {
    "protocol_handler.excluded_schemes.zoommtg": False,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("--headless")
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--v=1")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
async def join_zoom_meeting(meeting_url, user_name):
    global in_meeting
    driver.get(meeting_url)

    # driver.get_screenshot_as_file("screenshot_before_join.png")

    time.sleep(5)

    subprocess.run(["wmctrl", "-a", "Open xdg-open?"])
    time.sleep(1)

    time.sleep(1)
    subprocess.run(["xdotool", "key", "Tab"])
    subprocess.run(["xdotool", "key", "Tab"])
    subprocess.run(["xdotool", "key", "Tab"])

    # Click the Cancel button
    subprocess.run(["xdotool", "key", "Return"])

    time.sleep(5)

    try:
        # Accept cookies if necessary
        accept_cookies = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_cookies.click()
        print('cookies clicked successfully')
    except:
        print("No cookie consent button found, continuing...")

    # Click the "Join from Your Browser" link if available
    try:
        # join_browser_link = await driver.find_element(By.LINK_TEXT, "Launch Meeting")
        join_browser_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Join from your browser"))
        )
        print("Is displayed:", join_browser_link.is_displayed())
        print("Is enabled:", join_browser_link.is_enabled())


        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", join_browser_link)

        join_browser_link.click()
        time.sleep(5)
    except:
        print("No 'Join from Your Browser' option found, proceeding...")

    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "webclient"))  # Using the ID of the iframe
        )
        driver.switch_to.frame(iframe)
        print("Switched to iframe successfully.")
    except TimeoutException:
        print("Iframe not found within the time limit.")

    # Input the name in the Zoom join page
    try:
        name_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "preview-meeting-info-field-input"))
        )
        name_input.send_keys(user_name)  # Replace with the desired input
        print("Input field found using ID and value entered.")
    except TimeoutException:
        print("The input field with ID was not found or not clickable within the time limit.")

        # If ID approach fails, try using By.XPATH
        try:
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//label[text()='Your Name']/following-sibling::div/input"))
            )
            name_input.send_keys(user_name)  # Replace with the desired input
            print("Input field found using XPath and value entered.")
            time.sleep(5)
        except TimeoutException:
            print("The input field with XPath was not found or not clickable within the time limit.")

    # Click the "Join" button
    # driver.get_screenshot_as_file("screenshot_before.png")
    try:
        join_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "preview-join-button"))
        )
        join_button.click()
    except TimeoutException:
        print("First button not found, trying the second button.")

        # If the first fails, try to click the button using the ID
        try:
            join_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "joinBtn"))
            )
            join_button.click()
        except TimeoutException:
            print("Both button clicks failed.")

    time.sleep(5)

    try:
        popup_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "footer-button-base__img-layer"))
        )
        popup_element.click()
        join_audio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "join-audio-by-voip__join-btn"))
        )
        join_audio_button.click()
        print("Clicked 'Join Audio by Computer' button.")
        recorder.start_recording()
        print("Joined the Zoom meeting!")

    except TimeoutException:
        print("Join Audio button was not found or not clickable within the time limit.")

    try:
        leave_button =WebDriverWait(driver, 3600).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Leave']"))
        )
        print("Leave Is enabled:", leave_button.is_enabled())
        print("Meeting ongoing...")

        ok_button = WebDriverWait(driver, 3600).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".zm-btn.zm-btn--primary.zm-btn__outline--blue"))
         )

        # Click the OK button
        ok_button.click()
        print("OK button clicked, popup closed.")

        # Now wait for the "Leave" button to disappear, indicating the meeting has ended
        WebDriverWait(driver, 3600).until_not(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Leave']"))
        )
        print("Meeting ended.")
        recorder.stop_recording(file_path='zoom_meeting_recording.wav')
    except Exception as e:
        print(f"Error: {e}")

    finally:
        global in_meeting
        print("Meeting ended. Bot is ready to check for new meetings.")
        # driver.quit()
        return False

