import asyncio
import os
import pytest

from flexmock import flexmock

from file_downloader import downloader


@pytest.yield_fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


def test_download_file(event_loop, tmpdir):
    file = tmpdir.join('input.file')
    file.write(
        b'https://openclipart.org/assets/images/images/openclipart-banner.png')
    downloader.AsyncIODownloader(str(file), str(tmpdir)).run()
    assert 'openclipart-banner.png' in [f.basename for f in tmpdir.listdir()]
    assert tmpdir.join('openclipart-banner.png').size() == 6494


@pytest.mark.parametrize('destination,filename,expected', [
    ('.', 'image.png', './image.png'),
    ('/some/destination', 'image.png', '/some/destination/image.png'),
    (os.path.dirname(__file__), 'test_downloader.py',
     os.path.join(os.path.dirname(__file__), 'test_downloader-now.py')),
])
def test_get_filepath(destination, filename, expected):
    flexmock(downloader).should_receive('get_timestamp').and_return('now')
    assert downloader.AsyncIODownloader(None, destination)._get_filepath(
        'https://test.url/' + filename) == expected
