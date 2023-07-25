import re
from bs4 import BeautifulSoup
import requests


def check_string_format(input_string, keywords, country_name):
    keyword_pattern = "|".join(map(re.escape, keywords))
    pattern = rf"\w*/wiki/\w*({keyword_pattern})\w*_of_{country_name}"
    match = re.match(pattern, input_string)

    if match:
        matched_keyword = match.group(1)
    else:
        matched_keyword = "None"

    return bool(match), matched_keyword


def request_for_province(url, keyword):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    col_names = ["Province", "Region", "Name", "State", "name"]
    provinces = []
    col_index = 0

    heading_tag = soup.find(
        lambda tag: tag.name == "h2"
        and (keyword in tag.get_text() or "List" in tag.get_text())
    )

    if heading_tag:
        target_table = heading_tag.find_next("table")

        if target_table:
            all_tr_tags = target_table.find_all("tr")
            col_found = True

            for tr_tag in all_tr_tags:
                if not col_found:
                    break
                col_index = 0
                th_tags = tr_tag.find_all("th")

                for th_tag in th_tags:
                    if not col_found:
                        break
                    col_index += 1

                    for col_name in col_names:
                        if col_name in th_tag.get_text():
                            col_found = False
                            break
            provinces_found = False

            if not col_found:
                for tr_tag in all_tr_tags:
                    td_tags = tr_tag.find_all("td")

                    if len(td_tags) >= col_index:
                        td_tag = td_tags[col_index - 1]

                        for a_tag in td_tag.find_all(
                            "a", href=re.compile(r"^/wiki/[a-zA-Z_]+$")
                        ):
                            provinces.append(a_tag.get_text())
                            provinces_found = True

                        if not provinces_found:
                            text_content = td_tag.get_text(strip=True)
                            provinces.append(text_content)
                        else:
                            provinces_found = False
    return provinces


def get_provinces(soup, country_name):
    keywords = [
        "Provinces",
        "Regions",
        "Federative_units",
        "Federal_units",
        "States",
        "Federal_subjects",
        "Administrative_units",
    ]
    a_tags = soup.find_all("a")
    filtered_a_tag = ""
    key = None
    for tag in a_tags:
        flag, key = check_string_format(tag.get("href", ""), keywords, country_name)
        if flag:
            filtered_a_tag = tag["href"]
            break

    url = "https://en.wikipedia.org" + filtered_a_tag
    return request_for_province(url, key)