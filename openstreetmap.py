import overpy
import json
import re
from urllib.request import urlopen
from urllib.error import HTTPError

import file_utils


def save_json_map_data(query, filepath):
    """run overpass api http query and save response to file as json dict"""
    response = fetch_raw_http_response(overpass_query)
    json_data = file_utils.bytes_to_json(response)
    file_utils.save_json(json_data, filepath)


def save_raw_json_map_data(query, filepath):
    """run overpass api http query and save response to file as a raw byte stream of json data"""
    response = fetch_raw_http_response(overpass_query)
    file_utils.save_bytes(response, filepath)


def fetch_raw_http_response(query):
    """run overpass api http query and returns raw http response byte stream

    This is the same function used in overpy.query, except it doesn't parse the result
    """

    max_retry_count = 0
    read_chunk_size = 4096
    retry_timeout = 1.0
    url = "http://overpass-api.de/api/interpreter"
    regex_extract_error_msg = re.compile(b"\<p\>(?P<msg>\<strong\s.*?)\</p\>")
    regex_remove_tag = re.compile(b"<[^>]*?>")

    if not isinstance(query, bytes):
        query = query.encode("utf-8")

    retry_num = 0
    retry_exceptions = []
    do_retry = True if max_retry_count > 0 else False
    while retry_num <= max_retry_count:
        if retry_num > 0:
            time.sleep(retry_timeout)
        retry_num += 1
        try:
            f = urlopen(url, query)
        except HTTPError as e:
            f = e

        response = f.read(read_chunk_size)
        while True:
            data = f.read(read_chunk_size)
            if len(data) == 0:
                break
            response = response + data
        f.close()

        if f.code == 200:
            content_type = f.getheader("Content-Type")

            if content_type == "application/json":
                return response

            if content_type == "application/osm3s+xml":
                return response

            e = exception.OverpassUnknownContentType(content_type)
            if not do_retry:
                raise e
            retry_exceptions.append(e)
            continue

        if f.code == 400:
            msgs = []
            for msg in regex_extract_error_msg.finditer(response):
                tmp = regex_remove_tag.sub(b"", msg.group("msg"))
                try:
                    tmp = tmp.decode("utf-8")
                except UnicodeDecodeError:
                    tmp = repr(tmp)
                msgs.append(tmp)

            e = exception.OverpassBadRequest(
                query,
                msgs=msgs
            )
            if not do_retry:
                raise e
            retry_exceptions.append(e)
            continue

        if f.code == 429:
            e = exception.OverpassTooManyRequests
            if not do_retry:
                raise e
            retry_exceptions.append(e)
            continue

        if f.code == 504:
            e = exception.OverpassGatewayTimeout
            if not do_retry:
                raise e
            retry_exceptions.append(e)
            continue

        e = exception.OverpassUnknownHTTPStatusCode(f.code)
        if not do_retry:
            raise e
        retry_exceptions.append(e)
        continue

    raise exception.MaxRetriesReached(retry_count=retry_num, exceptions=retry_exceptions)


if __name__ == '__main__':
    api = overpy.Overpass()
    overpass_query = """
        [out:json];
        way(40.73489,-73.99264,40.74020,-73.97923) ["highway"];
        (._;>;);
        out;
        """

    # run query and save data locally
    save_raw_json_map_data(overpass_query, "map_data.txt")

    # load previously saved data from file
    result = api.parse_json(file_utils.load_bytes("map_data.txt"))

    # run query, parse results, and store result object in memory
    result = api.query(overpass_query)

    street_names = set()
    for way in result.ways:
        street_names.add(way.tags.get("name", "n/a"))
        # print("Name: %s" % way.tags.get("name", "n/a"))
        # print("  Highway: %s" % way.tags.get("highway", "n/a"))
        # print("  Nodes:")
        # for node in way.nodes:
        #     print("    Lat: %f, Lon: %f" % (node.lat, node.lon))

    for street in sorted(street_names):
        print(street)
