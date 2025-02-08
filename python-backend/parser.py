from playwright.async_api import async_playwright


async def search_corporation(company_name, num_results=1):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # Go to the search by name page
        await page.goto("https://search.sunbiz.org/Inquiry/CorporationSearch/ByName")

        # Enter search term
        search_box = page.locator('input[id="SearchTerm"]')
        await search_box.type(company_name, delay=10)
        await search_box.press("Enter")

        # Click on the first result
        links = await page.locator("#search-results tbody tr a").element_handles()
        if len(links) == 0:
            raise ValueError("Search returned no results")

        await links[0].click()

        corps = []
        for i in range(num_results):
            # Parse Detail Page
            corp_details = {}
            detail_sections = page.locator("div.detailSection")
            for detail_section in await detail_sections.all():
                paragraphs = await detail_section.locator("p").all()
                if len(paragraphs) == 2:
                    corp_details["corp_type"] = await paragraphs[0].inner_text()
                    corp_details["corp_name"] = await paragraphs[1].inner_text()
                    if (
                        corp_details["corp_type"] == "Trademark"
                    ):  # Trademarks have a different format and thus out of scope
                        break
                    continue

                spans = await detail_section.locator("span").all()
                if len(spans) > 0:
                    title = await spans[0].inner_text()
                    if title == "Filing Information":
                        corp_details["filing_info"] = []
                        labels = await detail_section.locator("div label").all()
                        spans = await detail_section.locator("div span").all()
                        if len(labels) != len(spans):
                            raise ValueError("Filing Information has mismatched labels")
                        for i in range(len(labels)):
                            corp_details["filing_info"].append(
                                {
                                    "internal_name": await labels[i].get_attribute(
                                        "for"
                                    ),
                                    "name": await labels[i].inner_text(),
                                    "value": await spans[i].inner_text(),
                                }
                            )
                    elif title == "Principal Address":
                        if len(spans) > 1:
                            corp_details["principal_addr"] = await spans[1].inner_text()
                        if len(spans) > 2:
                            changed = (await spans[2].inner_text()).split("Changed: ")
                            if len(changed) != 2:
                                continue
                            #                                raise ValueError("Changed date is invalid")
                            corp_details["principal_addr_changed"] = changed[1]
                    elif title == "Mailing Address":
                        if len(spans) > 1:
                            corp_details["mailing_addr"] = await spans[1].inner_text()
                        if len(spans) > 2:
                            changed = (await spans[2].inner_text()).split("Changed: ")
                            if len(changed) != 2:
                                continue
                            #                                raise ValueError("Changed date is invalid")
                            corp_details["mailing_addr_changed"] = changed[1]
                    elif title == "Registered Agent Name & Address":
                        if len(spans) > 2:
                            corp_details["registered_name"] = await spans[
                                1
                            ].inner_text()
                            corp_details["registered_addr"] = await spans[
                                2
                            ].inner_text()
                        if len(spans) > 3:
                            for span in spans[3:]:
                                changed = (await span.inner_text()).split(" Changed: ")
                                if len(changed) != 2:
                                    continue
                                #                                    raise ValueError("Changed date is invalid")
                                if changed[0] == "Name":
                                    corp_details["registered_name_changed"] = changed[1]
                                if changed[0] == "Address":
                                    corp_details["registered_addr_changed"] = changed[1]
                    elif title == "Officer/Director Detail":
                        corp_details["officers"] = []
                        for span in (await detail_section.inner_text()).split("\n"):
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
                                        corp_details["officers"][-1][
                                            "address"
                                        ] = span_text
                                    else:
                                        corp_details["officers"][-1]["address"] += (
                                            "\n" + span_text
                                        )
                    elif title == "Annual Reports":
                        rows = await detail_section.locator("tr").all()
                        corp_details["annual_reports"] = []
                        for row in rows[1:]:
                            cells = await row.locator("td").all()
                            if len(cells) != 2:
                                raise ValueError(
                                    "Annual Reports table has unexpected number of columns"
                                )
                            corp_details["annual_reports"].append(
                                {
                                    "report_year": await cells[0].inner_text(),
                                    "filing_date": await cells[1].inner_text(),
                                }
                            )
                    elif title == "Document Images":
                        rows = await detail_section.locator("tr").all()
                        corp_details["documents"] = []
                        for row in rows[1:]:
                            cells = await row.locator("td").all()
                            if len(cells) != 2:
                                raise ValueError(
                                    "Document Images table has unexpected number of columns"
                                )
                            report_link = cells[0].locator("a")
                            corp_details["documents"].append(
                                {
                                    "title": await report_link.inner_text(),
                                    "link": f"https://search.sunbiz.org/{await report_link.get_attribute("href")}",
                                }
                            )
            else:
                corps.append(corp_details)
            next_page_link = await page.locator(
                'a[title="Next On List"]'
            ).element_handles()
            if len(next_page_link) == 0:
                break
            else:
                await next_page_link[0].click()
        return corps


if __name__ == "__main__":
    print(search_corporation("Fighters, Inc"))
