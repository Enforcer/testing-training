import time
from multiprocessing import Process
from contextlib import contextmanager
from typing import Iterator

import httpx

import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


@contextmanager
def running_server(port: int, timeout_s: int = 5) -> Iterator[None]:
    server_process = Process(
        target=uvicorn.run,
        kwargs={"app": "testing_training.machine.resupplier_app.app:app", "port": port},
        daemon=True,
    )
    server_process.start()
    start_time = time.monotonic()

    # Wait until server runs
    while start_time + timeout_s > time.monotonic():
        try:
            response = httpx.get(f"http://localhost:{port}")
            response.raise_for_status()
            break
        except httpx.HTTPError:
            time.sleep(0.05)
            continue
    if start_time + timeout_s <= time.monotonic():
        raise TimeoutError("Server did not start in time")

    yield
    server_process.terminate()


def test_if_machine_status_can_be_changed(unused_tcp_port: int) -> None:
    with running_server(unused_tcp_port, timeout_s=5):
        driver = webdriver.Firefox()
        try:
            driver.get(f"http://localhost:{unused_tcp_port}")
            element = driver.find_element(By.XPATH, "//select[@name='machine_status']")
            select = Select(element)
            select.select_by_value("out_of_order")
            driver.find_element(By.ID, "submit").click()

            # Page gets reloaded
            element = driver.find_element(By.XPATH, "//select[@name='machine_status']")
            select = Select(element)
            assert select.first_selected_option.get_attribute("value") == "out_of_order"
        finally:
            driver.quit()


def test_if_machine_status_can_be_changed_on_chrome(unused_tcp_port: int) -> None:
    with running_server(unused_tcp_port, timeout_s=5):
        driver = webdriver.Chrome()
        try:
            driver.get(f"http://localhost:{unused_tcp_port}")
            element = driver.find_element(By.XPATH, "//select[@name='machine_status']")
            select = Select(element)
            select.select_by_value("out_of_order")
            driver.find_element(By.ID, "submit").click()

            # Page gets reloaded
            element = driver.find_element(By.XPATH, "//select[@name='machine_status']")
            select = Select(element)
            assert select.first_selected_option.get_attribute("value") == "out_of_order"
        finally:
            driver.quit()
