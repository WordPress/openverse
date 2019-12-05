import Flickr
from datetime import datetime
import os

def test_getMetaData(monkeypatch):
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    def mockresult(a_url):
        return {
            "photos": {
                "page": 1,
                "pages": 1,
                "perpage": 500,
                "total": "2",
                "photo": [
                    {
                        "id": "123",
                        "owner": "123@N07",
                        "title": "rpk 10 ans-8",
                        "license": "3",
                        "description": {
                            "_content": ""
                        },
                        "dateupload": "1572340565",
                        "datetaken": "2019-09-07 16:27:59",
                        "ownername": "Tom-C photographe",
                        "tags": "",
                        "url_t": "https://live.staticflickr.com/123_t.jpg",
                        "height_t": 100,
                        "width_t": 75,
                        "url_s": "https://live.staticflickr.com/123_m.jpg",
                        "height_s": 240,
                        "width_s": 180,
                        "url_m": "https://live.staticflickr.com/123.jpg",
                        "height_m": 500,
                        "width_m": 375,
                        "url_l": "https://live.staticflickr.com/123_b.jpg",
                        "height_l": 1024,
                        "width_l": 768
                    },
                    {
                        "id": "456",
                        "owner": "456@N04",
                        "title": "233 Ordesa sept 2019",
                        "license": "3",
                        "description": {
                            "_content": "OLYMPUS DIGITAL CAMERA"
                        },
                        "dateupload": "1571326372",
                        "datetaken": "2019-09-07 16:26:44",
                        "ownername": "RADIOfotoGRAFIANDO",
                        "tags": "amarilla",
                        "url_t": "https://live.staticflickr.com/456_t.jpg",
                        "height_t": 75,
                        "width_t": 100,
                        "url_s": "https://live.staticflickr.com/456_m.jpg",
                        "height_s": 180,
                        "width_s": 240,
                        "url_m": "https://live.staticflickr.com/456.jpg",
                        "height_m": 375,
                        "width_m": 500,
                        "url_l": "https://live.staticflickr.com/456_b.jpg",
                        "height_l": 768,
                        "width_l": 1024
                    },
                ]
            },
            "stat": "ok"
        }
    tmp_directory = '/tmp/'
    output_filename = 'flickr_test.tsv'
    monkeypatch.setattr(Flickr, "requestContent", mockresult)
    monkeypatch.setattr(Flickr.writeToFile, '__defaults__', (tmp_directory,))
    monkeypatch.setattr(Flickr, "FILE", output_filename)
    output_fullpath = os.path.join(tmp_directory, output_filename)
    try:
        os.remove(output_fullpath)
    except:
        print("Could not delete old output.  Perhaps it does not exist yet.")
    expected_records = 2
    actual_records = Flickr.getMetaData(cur_time, nxt_time, 'potato')
    assert expected_records == actual_records
    expected_filestring = """123\twww.flickr.com/photos/123@N07/123\thttps://live.staticflickr.com/123_b.jpg\thttps://live.staticflickr.com/123_m.jpg\t768\t1024\t\\N\tby-nc-nd\t2.0\tTom-C photographe\twww.flickr.com/photos/123@N07\trpk 10 ans-8\t{"pub_date": "1572340565", "date_taken": "2019-09-07 16:27:59"}\t\\N\tf\tflickr\tflickr\n456\twww.flickr.com/photos/456@N04/456\thttps://live.staticflickr.com/456_b.jpg\thttps://live.staticflickr.com/456_m.jpg\t1024\t768\t\\N\tby-nc-nd\t2.0\tRADIOfotoGRAFIANDO\twww.flickr.com/photos/456@N04\t233 Ordesa sept 2019\t{"pub_date": "1571326372", "date_taken": "2019-09-07 16:26:44", "description": "OLYMPUS DIGITAL CAMERA"}\t[{"name": "amarilla", "provider": "flickr"}]\tf\tflickr\tflickr\n"""
    with open(output_fullpath) as f:
        actual_filestring = f.read()
    assert expected_filestring == actual_filestring
