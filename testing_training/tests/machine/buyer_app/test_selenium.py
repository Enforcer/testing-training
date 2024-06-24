import time
from pathlib import Path

import pytest
from selenium import webdriver
from multiprocessing import Process
from typing import Iterator, Callable

import httpx
import uvicorn
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from testing_training.machine.database import Session
from testing_training.machine.inventory import set_stock_on_engine
from testing_training.machine.products import add_product, Money, list_products
from testing_training.machine.products.money import Currency
from testing_training.tests.machine.buyer_app import tools


EXAMPLE_IMAGE = Path(__file__).parent / "files/img.png"


@pytest.mark.usefixtures("clean_db", "running_server")
def test_buying_the_only_available_item_makes_it_out_of_stock(
    unused_tcp_port: int
) -> None:
    url = f"http://localhost:{unused_tcp_port}"
    wait_until(lambda: server_runs(unused_tcp_port), 5)
    tools.restore_terminal()
    tools.restore_engine_state()

    add_product(
        name="Example",
        description="No description for example product!",
        price=Money(10, Currency.PLN),
        image=EXAMPLE_IMAGE.read_bytes(),
    )
    products = list_products()
    product_id = products[0].id
    set_stock_on_engine(row=1, column=1, product_id=product_id, quantity=1)
    Session().commit()

    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    try:
        driver.get(url)
        first_product = driver.find_element(By.CSS_SELECTOR, "button.see-product")
        first_product.click()

        add_to_cart_btn = driver.find_element(By.CSS_SELECTOR, "button.add-to-cart")
        add_to_cart_btn.click()

        go_to_cart = driver.find_element(By.CSS_SELECTOR, ".go-to-cart")
        go_to_cart.click()

        purchase_btn = driver.find_element(By.CSS_SELECTOR, "button.purchase-btn")
        purchase_btn.click()

        WebDriverWait(driver, 5).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.checkout-header"),
                "Use your card to pay"
            )
        )

        WebDriverWait(driver, 5).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.checkout-header"),
                "All good"
            )
        )

        WebDriverWait(driver, 10).until(
            expected_conditions.url_contains("/products")
        )

        products_title = driver.find_element(By.CSS_SELECTOR, ".product-title")
        assert "Out Of Stock" in products_title.text
    finally:
        driver.quit()


@pytest.mark.usefixtures("clean_db", "running_server")
def test_buying_the_one_of_two_available_items_makes_stock_fall_to_1(
    unused_tcp_port: int
) -> None:
    url = f"http://localhost:{unused_tcp_port}"
    wait_until(lambda: server_runs(unused_tcp_port), 5)
    tools.restore_terminal()
    tools.restore_engine_state()

    add_product(
        name="Example",
        description="No description for example product!",
        price=Money(10, Currency.PLN),
        image=EXAMPLE_IMAGE.read_bytes(),
    )
    products = list_products()
    product_id = products[0].id
    set_stock_on_engine(row=1, column=1, product_id=product_id, quantity=2)
    Session().commit()

    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    try:
        driver.get(url)
        first_product = driver.find_element(By.CSS_SELECTOR, "button.see-product")
        first_product.click()

        add_to_cart_btn = driver.find_element(By.CSS_SELECTOR, "button.add-to-cart")
        add_to_cart_btn.click()

        go_to_cart = driver.find_element(By.CSS_SELECTOR, ".go-to-cart")
        go_to_cart.click()

        purchase_btn = driver.find_element(By.CSS_SELECTOR, "button.purchase-btn")
        purchase_btn.click()

        WebDriverWait(driver, 5).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.checkout-header"),
                "Use your card to pay"
            )
        )

        WebDriverWait(driver, 5).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.checkout-header"),
                "All good"
            )
        )

        WebDriverWait(driver, 10).until(
            expected_conditions.url_contains("/products")
        )

        first_product = driver.find_element(By.CSS_SELECTOR, "button.see-product")
        first_product.click()
        in_stock_info = driver.find_element(By.CSS_SELECTOR, ".remaining-stock")
        assert "1" in in_stock_info.text
    finally:
        driver.quit()


@pytest.mark.usefixtures("clean_db", "running_server")
def test_payment_error_is_displayed_when_payment_terminal_is_malfunctioning(
    unused_tcp_port: int
) -> None:
    url = f"http://localhost:{unused_tcp_port}"
    wait_until(lambda: server_runs(unused_tcp_port), 5)
    tools.restore_terminal()
    tools.restore_engine_state()

    add_product(
        name="Example",
        description="No description for example product!",
        price=Money(10, Currency.PLN),
        image=EXAMPLE_IMAGE.read_bytes(),
    )
    products = list_products()
    product_id = products[0].id
    set_stock_on_engine(row=1, column=1, product_id=product_id, quantity=1)
    Session().commit()

    tools.simulate_terminal_malfunction()

    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    try:
        driver.get(url)
        first_product = driver.find_element(By.CSS_SELECTOR, "button.see-product")
        first_product.click()

        add_to_cart_btn = driver.find_element(By.CSS_SELECTOR, "button.add-to-cart")
        add_to_cart_btn.click()

        go_to_cart = driver.find_element(By.CSS_SELECTOR, ".go-to-cart")
        go_to_cart.click()

        purchase_btn = driver.find_element(By.CSS_SELECTOR, "button.purchase-btn")
        purchase_btn.click()

        WebDriverWait(driver, 5).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.checkout-header"),
                "There was a problem with the payment"
            )
        )

        WebDriverWait(driver, 10).until(
            expected_conditions.url_contains("/products")
        )
    finally:
        driver.quit()


@pytest.fixture
def running_server(unused_tcp_port: int) -> Iterator[None]:
    server_process = Process(
        target=uvicorn.run,
        kwargs={"app": "testing_training.machine.buyer_app.app:app", "port": unused_tcp_port},
        daemon=True,
    )
    server_process.start()
    yield
    server_process.terminate()


def wait_until(condition: Callable[[], bool], timeout: int = 5) -> None:
    """Waits until condition is met"""
    __tracebackhide__ = True

    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if condition():
            return
        time.sleep(0.1)

    pytest.fail(f"Condition {condition.__name__} was not met in time!")


def server_runs(port: int) -> bool:
    __tracebackhide__ = True

    try:
        response = httpx.get(f"http://localhost:{port}")
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False
