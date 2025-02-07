from playwright.sync_api import sync_playwright


def search_company_by_name(company_name):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Go to the search by name page
        page.goto("https://search.sunbiz.org/Inquiry/CorporationSearch/ByName")

        # Enter search term
        search_box = page.locator('input[id="SearchTerm"]')
        search_box.type(company_name, delay=10)
        search_box.press("Enter")

        # Click on the first result
        links = page.locator("#search-results tbody tr a").element_handles()
        if len(links) > 0:
            links[0].click()

        # Parse Detail Page
        corp_details = {}
        detail_sections = page.locator("div.detailSection")
        for detail_section in detail_sections.all():
            paragraphs = detail_section.locator("p").all()
            if len(paragraphs) == 2:
                corp_details["corp_type"] = paragraphs[0].inner_text()
                corp_details["corp_name"] = paragraphs[1].inner_text()
                continue

            spans = detail_section.locator("span").all()
            if len(spans) > 0:
                title = spans[0].inner_text()
                if title == "Filing Information":
                    corp_details["filing_info"] = []
                    labels = detail_section.locator("div label").all()
                    spans = detail_section.locator("div span").all()
                    if len(labels) != len(spans):
                        raise ValueError("Filing Information has mismatched labels")
                    for i in range(len(labels)):
                        corp_details["filing_info"].append(
                            {
                                "internal_name": labels[i].get_attribute("for"),
                                "name": labels[i].inner_text(),
                                "value": spans[i].inner_text(),
                            }
                        )
                elif title == "Principal Address":
                    if len(spans) > 1:
                        corp_details["principal_addr"] = spans[1].inner_text()
                    if len(spans) > 2:
                        changed = spans[2].inner_text().split("Changed: ")
                        if len(changed) != 2:
                            raise ValueError("Changed date is invalid")
                        corp_details["principal_addr_changed"] = changed[1]
                elif title == "Mailing Address":
                    if len(spans) > 1:
                        corp_details["mailing_addr"] = spans[1].inner_text()
                    if len(spans) > 2:
                        changed = spans[2].inner_text().split("Changed: ")
                        if len(changed) != 2:
                            raise ValueError("Changed date is invalid")
                        corp_details["mailing_addr_changed"] = changed[1]
                elif title == "Registered Agent Name & Address":
                    if len(spans) > 2:
                        corp_details["registered_name"] = spans[1].inner_text()
                        corp_details["registered_addr"] = spans[2].inner_text()
                    if len(spans) > 3:
                        for span in spans[3:]:
                            changed = span.inner_text().split(" Changed: ")
                            if len(changed) != 2:
                                raise ValueError("Changed date is invalid")
                            if changed[0] == "Name":
                                corp_details["registered_name_changed"] = changed[1]
                            if changed[0] == "Address":
                                corp_details["registered_addr_changed"] = changed[1]
                elif title == "Officer/Director Detail":
                    corp_details["officers"] = []
                    for span in detail_section.inner_text().split("\n"):
                        if span.strip() == "":
                            continue
                        span_text = span
                        if "Title " in span_text:
                            corp_details["officers"].append(
                                {"title": span_text.split("Title ")[1]}
                            )
                        else:
                            if len(corp_details["officers"]) == 0:
                                continue
                            if len(corp_details["officers"][-1]) == 1:
                                corp_details["officers"][-1]["name"] = span_text
                            elif len(corp_details["officers"][-1]) > 1:
                                if "address" not in corp_details["officers"][-1]:
                                    corp_details["officers"][-1]["address"] = span_text
                                else:
                                    corp_details["officers"][-1]["address"] += (
                                        "\n" + span_text
                                    )
                elif title == "Annual Reports":
                    rows = detail_section.locator("tr").all()
                    corp_details["annual_reports"] = []
                    for row in rows[1:]:
                        cells = row.locator("td").all()
                        if len(cells) != 2:
                            raise ValueError(
                                "Annual Reports table has unexpected number of columns"
                            )
                        corp_details["annual_reports"].append(
                            {
                                "report_year": cells[0].inner_text(),
                                "filed_date": cells[1].inner_text(),
                            }
                        )
                elif title == "Document Images":
                    rows = detail_section.locator("tr").all()
                    corp_details["documents"] = []
                    for row in rows[1:]:
                        cells = row.locator("td").all()
                        if len(cells) != 2:
                            raise ValueError(
                                "Document Images table has unexpected number of columns"
                            )
                        report_link = cells[0].locator("a")
                        corp_details["documents"].append(
                            {
                                "title": report_link.inner_text(),
                                "link": report_link.get_attribute("href"),
                            }
                        )
        return corp_details


if __name__ == "__main__":
    print(search_company_by_name("Fighters, Inc"))
