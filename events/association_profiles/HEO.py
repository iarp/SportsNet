"""
    I've left this script unfinished. HEO does not publish the sanction number
    on the main search table, you must visit each events page to get that number.
    I do not want to be hitting their site once a week and then hitting 100+ event
    pages to check and see if we already have the sanction number in our system.
    I let Nathan know HEO is not possible for the time being.

    Why not match on title? What happens if the same title was used last year?
    Why not match on date and title? What happens when either of those values
    change, even in the slightest?

    It scans the first page (i did not add the system to follow to the next page) and
    finds the events sanction number on the events page.
"""
import datetime
import logging
import traceback

from bs4 import BeautifulSoup

from browser import SKBrowserBase

# from selenium.common.exceptions import WebDriverException

log = logging.getLogger("events.commands.get_tournament_listing")

ENABLED = False


def scan(browser: SKBrowserBase, association):

    raise ValueError("HEO is disabled at this time.")

    # try:
    #     browser.wait_until(element_id='edit-submit-tournament-listing')
    # except AttributeError:
    #     log.debug(f'Unable to find Apply button with id="edit-submit-tournament-listing", skipping site: {association.name} {association.tournament_listing_url}')
    #     return None
    # except WebDriverException:
    #     try:
    #         browser.save_screenshot(sub_folder='WebDriverException')
    #     except:
    #         log.debug(traceback.format_exc())
    #     return None

    # with open('cache/heo-listing.html', 'w') as fw:
    #     fw.write(browser.browser.page_source)
    with open("cache/heo-listing.html", "r") as fo:
        source = fo.read()

    # soup = BeautifulSoup(browser.browser.page_source, "html.parser")
    soup = BeautifulSoup(source, "html.parser")

    table = soup.find("table", {"class": "views-table"})
    table_body = table.find("tbody")

    columns = ["Date", "Tournament Name", "HLComp", "BodyChk", "Divisions"]

    rows = []

    for row_index, row in enumerate(table_body.find_all("tr")):
        row_data = {}

        cols = [ele.text.strip() for ele in row.find_all("td")]

        if not row_index:
            continue

        for index, col in enumerate(columns):
            row_data[col] = cols[index]

        link_to_event = row.find("td", {"class": "views-field-title"}).find(
            "a", href=True
        )["href"]
        link_to_event = f"http://www.heominor.ca{link_to_event}"

        try:
            start_raw, end_raw = row_data["Date"].split(" to ", 1)

            row_data["Start Date"] = datetime.datetime.strptime(
                start_raw, "%b %d %Y"
            ).date()

            try:
                row_data["End Date"] = datetime.datetime.strptime(
                    end_raw, "%b %d %Y"
                ).date()
            except ValueError:
                row_data["End Date"] = row_data["Start Date"]

        except ValueError:
            log.debug(traceback.format_exc())
            log.debug(
                "{}: bad Start/End dates, expecting dd-Mth-YYYY, received {} and {}".format(
                    association.name, row_data["Start Date"], row_data["End Date"]
                )
            )
            continue

        print(row)
        print(row_data)

        browser.load_url(link_to_event)
        with open("cache/heo-listing-event.html", "w") as fw:
            fw.write(browser.browser.page_source)
        # with open('cache/heo-listing-event.html', 'r') as fo:
        #     source = fo.read()

        soup = BeautifulSoup(browser.browser.page_source, "html.parser")
        # soup = BeautifulSoup(source, 'html.parser')

        sanction_number = (
            soup.find("div", {"class": "field-name-field-sanction-number"})
            .find("div", {"class": "field-items"})
            .text
        )

        row_data["Sanction Number"] = sanction_number

        return
