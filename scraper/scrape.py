from collections import namedtuple
import os
from result import Ok, Err, Result
from pymongo import MongoClient
import requests

from utils import MongoCollection, get_mongo_scrape_db, upload_to_mongo

HousePageInfo = namedtuple("House_Page_info", ["page_count", "page", "data"])


def get_housing_data_at(page: int = 0) -> Result[HousePageInfo, str]:
    URL = os.environ.get("ENDPOINT")
    if not URL:
        return Err(
            "No url endpoint found. Please use the ENDPOINT environment variable"
        )
    offset = str(page * 50)

    headers = {
        "Connection": "keep-alive",
        "accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "content-type": "application/json",
        "Sec-GPC": "1",
        "Origin": "https://qasa.se",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://qasa.se/",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "dnt": "1",
    }

    data = '{"operationName":"HomeSearchQuery","variables":{"limit":50,"platform":"qasa","searchParams":{"householdSize":1,"shared":false,"minSquareMeters":15,"minRentalLength":31536000,"areaIdentifier":["se/stockholm"]},"offset":**offset**,"order":"DESCENDING","orderBy":"PUBLISHED_AT"},"query":"query HomeSearchQuery($offset: Int, $limit: Int, $platform: PlatformEnum!, $order: HomeSearchOrderEnum, $orderBy: HomeSearchOrderByEnum, $searchParams: HomeSearchParamsInput!) {\\n  homeSearch(\\n    platform: $platform\\n    searchParams: $searchParams\\n    order: $order\\n    orderBy: $orderBy\\n  ) {\\n    filterHomesOffset(offset: $offset, limit: $limit) {\\n      pagesCount\\n      totalCount\\n      hasNextPage\\n      hasPreviousPage\\n      nodes {\\n        id\\n        firsthand\\n        rent\\n        tenantBaseFee\\n        title\\n        landlord {\\n          uid\\n          companyName\\n          premium\\n          professional\\n          profilePicture {\\n            url\\n            __typename\\n          }\\n          proPilot\\n          __typename\\n        }\\n        location {\\n          latitude\\n          longitude\\n          route\\n          locality\\n          sublocality\\n          __typename\\n        }\\n        links {\\n          locale\\n          url\\n          __typename\\n        }\\n        roomCount\\n        seniorHome\\n        shared\\n        squareMeters\\n        studentHome\\n        type\\n        duration {\\n          createdAt\\n          endOptimal\\n          endUfn\\n          id\\n          startAsap\\n          startOptimal\\n          updatedAt\\n          __typename\\n        }\\n        corporateHome\\n        uploads {\\n          id\\n          url\\n          type\\n          title\\n          metadata {\\n            primary\\n            order\\n            __typename\\n          }\\n          __typename\\n        }\\n        numberOfHomes\\n        minRent\\n        maxRent\\n        minRoomCount\\n        maxRoomCount\\n        minSquareMeters\\n        maxSquareMeters\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    response = requests.post(
        URL, headers=headers, data=data.replace("**offset**", offset)
    )
    raw = response.json()
    match raw:
        case {
            "data": {
                "homeSearch": {
                    "filterHomesOffset": {"pagesCount": pagecount, "nodes": data}
                }
            }
        }:
            return Ok(HousePageInfo(pagecount, page, data))
    return Err("Data not valid at page:{} offset:{}".format(page, offset))


def scrape() -> Result[str, str]:
    def update_db(data):
        duplicates = get_dupplicates(data, MongoCollection.HomeSearch)
        data = list(filter(lambda item: item["id"] not in duplicates, data))
        if not data:
            return duplicates
        print("Upload {} new entries".format(len(data)))
        upload_to_mongo(data, MongoCollection.HomeSearch)
        return duplicates

    info = get_housing_data_at()
    if isinstance(info, Err):
        return info

    pagecount, _, data = info.unwrap()
    print("Page count: ", pagecount)
    duplicates = update_db(data)
    print("Page {} is uploaded".format(1))
    if len(duplicates) > 0:
        return Ok("ok")

    for i in range(1, pagecount):
        info = get_housing_data_at(i)
        if isinstance(info, Err):
            return info

        pagecount, _, data = info.unwrap()

        duplicates = update_db(data)
        print("Page {} is uploaded".format(i + 1))
        if len(duplicates) > 0:
            break

    return Ok("ok")


# @as_result()
def get_dupplicates(data, collection):
    client = get_mongo_scrape_db()
    db = client[collection]

    keys = [item.get("id") for item in data]

    duplicates = db.find({"id": {"$in": keys}})

    return [item["id"] for item in duplicates]




def scrape_locations():
    headers = {
        "Connection": "keep-alive",
        "accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
        "content-type": "application/json",
        "Sec-GPC": "1",
        "Origin": "https://qasa.se",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://qasa.se/",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "dnt": "1",
    }

    data = '{"operationName":"HomeSearchCoordsQuery","variables":{"filterOnArea":false,"platform":"qasa","searchParams":{"areaIdentifier":["se/stockholm"]}},"query":"query HomeSearchCoordsQuery($platform: PlatformEnum!, $searchParams: HomeSearchParamsInput, $filterOnArea: Boolean) {\\n  homeSearchCoords(\\n    platform: $platform\\n    searchParams: $searchParams\\n    filterOnArea: $filterOnArea\\n  ) {\\n    filterHomesRaw\\n    __typename\\n  }\\n}\\n"}'

    response = requests.post("https://api.qasa.se/graphql", headers=headers, data=data)


if __name__ == "__main__":
    match scrape():
        case Ok(a):
            print("Success :", a)
        case Err(e):
            print("Error :", e)
