from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import csv
import json

# Replace with your actual Amazon credentials (for testing purposes only)
# **WARNING:** Do not use real credentials for long-term use or in production.
# Amazon may block accounts for automated scraping.
USERNAME = "your_test_username"  # Replace with a valid test username
PASSWORD = "your_test_password"  # Replace with a valid test password

# Base URL for Amazon India
BASE_URL = "https://www.amazon.in/"

def login(driver):
    driver.get(BASE_URL)
    try:
        # Find and click the account & lists button
        account_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList"))
        )
        account_button.click()

        # Find and click the sign-in button
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        sign_in_button.click()

        # Enter username and password
        username_field = driver.find_element(By.ID, "ap_email")
        username_field.send_keys(USERNAME)
        continue_button = driver.find_element(By.ID, "continue")
        continue_button.click()

        password_field = driver.find_element(By.ID, "ap_password")
        password_field.send_keys(PASSWORD)
        sign_in_button = driver.find_element(By.ID, "signInSubmit")
        sign_in_button.click()

        # Wait for login to complete
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "nav-logo"))
        )
        print("Login successful.")

    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        exit()

def get_categories(driver):
    driver.get(f"{BASE_URL}gp/bestsellers/?ref_=nav_em_cs_bestsellers_0_1_1_2")
    categories = []
    try:
        category_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'zg_browse_link')]")
        for element in category_elements:
            category_url = element.get_attribute("href")
            category_name = element.text.strip()
            if "Best Sellers" not in category_name:
                categories.append(category_name.lower().replace(" ", "-"))
    except Exception as e:
        print(f"Error getting categories: {e}")
    return categories

def scrape_category(driver, category):
    try:
        driver.get(f"{BASE_URL}gp/bestsellers/{category}/ref=zg_bs_nav_{category}_0")
        products = []
        page_number = 1

        while True:
            print(f"Scraping page {page_number} of {category}")

            # Find product elements (adjust XPATH if necessary)
            product_elements = driver.find_elements(By.XPATH, "//div[contains(@data-asin, 'B')]")

            for product in product_elements:
                try:
                    product_name = product.find_element(By.XPATH, ".//span[@class='a-size-base-plus a-color-base a-text-normal']").text
                    try:
                        product_price = product.find_element(By.XPATH, ".//span[@class='a-offscreen']").text
                    except NoSuchElementException:
                        product_price = "N/A"
                    # ... (Extract other details as needed)

                    products.append({
                        "Product Name": product_name,
                        "Product Price": product_price,
                        # ... (Add other extracted details to the dictionary)
                    })

                except Exception as e:
                    print(f"Error scraping product: {e}")
                    continue

            # Go to the next page (if available)
            try:
                next_page_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'a-pagination-next')]"))
                )
                next_page_button.click()
                time.sleep(2)  # Add a small delay
                page_number += 1
            except NoSuchElementException:
                break

            # Limit scraping to top 1500 products (adjust as needed)
            if len(products) >= 1500:
                break

        return products

    except Exception as e:
        print(f"Error scraping category: {e}")
        return []

if __name__ == "__main__":
    try:
        driver = webdriver.Chrome()  # Replace with your preferred webdriver
        driver.maximize_window()

        login(driver)
        categories = get_categories(driver)

        all_products = []
        for category in categories:
            products = scrape_category(driver, category)
            all_products.extend(products)

        with open("amazon_in_bestsellers.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Product Name", "Product Price"]  # Add other fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_products)

        with open("amazon_in_bestsellers.json", "w", encoding="utf-8") as jsonfile:
            json.dump(all_products, jsonfile, indent=4)

        print("Scraping completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()