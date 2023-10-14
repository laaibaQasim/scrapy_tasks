import asyncio
import aiohttp
import requests
import re
from bs4 import BeautifulSoup
from provinces import get_provinces


# global variables
countries = []
country_links = []
link_pattern = re.compile(r"^/wiki/[A-Za-z_]+$")


def set_url_name_flag(rows):
    count_url = 0

    for row in rows:
        a_tag = row.select_one("td a")
        img_tag = row.select_one("td span.flagicon img")

        if a_tag and img_tag:
            country_link = a_tag["href"]

            if country_link == "#cite_note-11":
                a_tags = row.find_all("a")
                a_tag = a_tags[1]
                country_link = a_tag["href"]

            if re.match(link_pattern, country_link):
                country_link = "https://en.wikipedia.org" + country_link
                country = {"url": country_link}
                countries.append(country)
                countries[count_url]["name"] = a_tag.text
                flag_link = img_tag["src"]
                flag_link = "http:" + flag_link
                countries[count_url]["images"] = [flag_link]
                count_url += 1


def get_capital_name(soup):
    th_tags = soup.select("th")

    for th_tag in th_tags:
        if "Capital" in th_tag.text:
            td_tag = th_tag.find_next_sibling("td")

            if td_tag:
                a_tag = td_tag.find("a")

                if a_tag:
                    capital_name = a_tag.text
                    return capital_name

    return None


def get_lat_long(td_tag):
    span_lat = td_tag.find("span", class_="latitude")
    span_long = td_tag.find("span", class_="longitude")

    if span_lat and span_long:
        return span_lat.text, span_long.text

    return None, None


def emblem_name(soup):
    a_tag = soup.find(
        "a",
        attrs={
            "class": "mw-file-description",
            "title": lambda value: value
            and ("coat of arms" in value.lower() or "emblem" in value.lower()),
        },
    )

    if a_tag:
        img_tag = a_tag.find("img")

        if img_tag:
            img_src = img_tag["src"]
            return "http:" + img_src

    return None


async def main():
    """
    function which asynchronously sends request to each country's page and extract remaining information.
    """
    async with aiohttp.ClientSession() as session:
        for i in range(len(countries)):
            async with session.get(countries[i]["url"], ssl=False) as resp:
                countries[i]["response_code"] = resp.status

                if resp.status == 200:
                    html_text = await resp.text()
                    soup = BeautifulSoup(html_text, "html.parser")
                    countries[i]["images"].append(emblem_name(soup))
                    countries[i]["capital"] = get_capital_name(soup)
                    countries[i]["lat_long"] = get_lat_long(soup)
                    countries[i]["Provinces"] = get_provinces(
                        soup, countries[i]["name"]
                    )


if __name__ == "__main__":
    start_url = (
        "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area"
    )
    response = requests.get(start_url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="wikitable sortable")
    rows = table.select("tr")
    set_url_name_flag(rows)
    asyncio.run(main())

    for country in countries:
        print("{")
        for key, value in country.items():
            print(f"{key}: {value},")
        print("}")
