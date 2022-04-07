import datetime
import logging
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException

log = logging.getLogger("events.commands.get_tournament_listing")

ENABLED = True


def scan(browser, association):

    try:
        browser.wait_until(element_name="btnList")
    except AttributeError:
        log.exception(
            f'Unable to find submit button with name="btnList", skipping {association}'
        )
        return None
    except WebDriverException:
        try:
            browser.save_screenshot(sub_folder="WebDriverException")
        except:
            log.exception("Screenshot Failure")
        return None

    browser.get_element(element_name="btnList").click()

    time.sleep(2)

    soup = BeautifulSoup(browser.browser.page_source, "html.parser")

    table = soup.find("table", {"class": "tbl-tournament"})
    table_body = table.find("tbody")

    columns = [
        "Sanction Number",
        "Start Date",
        "End Date",
        "Tournament Name",
        "Centre",
        "Divisions",
        "Details",
    ]
    rows = []

    for row_index, row in enumerate(table_body.find_all("tr")):
        row_data = {}

        cols = [ele.text.strip() for ele in row.find_all("td")]

        if not row_index:
            continue

        for index, col in enumerate(columns):
            row_data[col] = cols[index]

        try:
            row_data["Start Date"] = datetime.datetime.strptime(
                row_data["Start Date"], "%d-%b-%Y"
            ).date()
        except ValueError:
            log.exception(
                "{}: bad Start/End dates, expecting dd-Mth-YYYY, received {} and {}".format(
                    association.name, row_data["Start Date"], row_data["End Date"]
                )
            )
            continue

        try:
            row_data["End Date"] = datetime.datetime.strptime(
                row_data["End Date"], "%d-%b-%Y"
            ).date()
        except ValueError:
            row_data["End Date"] = row_data["Start Date"]

        rows.append(row_data)

    return rows
