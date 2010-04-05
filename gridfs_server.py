#!/usr/bin/env python
import bottle
import pymongo
from gridfs import GridFS
from gridfs.errors import NoFile
import mimetypes
from itertools import imap
from operator import itemgetter

DB_NAME = 'test'
COLLECTION_PREFIX = 'fs'
CONNECTION = pymongo.Connection() # add host and port if needed
SERVER = bottle.AutoServer # see bottle.py for possible servers
DEBUG = False # don't print exceptions in http output

db = CONNECTION[DB_NAME]
fs = GridFS(db, COLLECTION_PREFIX)

@bottle.get('/:filename#.*#')
def serve_file(filename):
# Most of this is based on bottle.py's static_file function but modified for GridFS
    try:
        file = fs.get_last_version(filename)
    except NoFile:
        return bottle.HTTPError(404, "Not found:" + filename)

    content_type = file.content_type or mimetypes.guess_type(filename)[0]
    headers = {'Content-Type': content_type,
               'Content-Length': file.length,
               'Last-Modified': file.upload_date.strftime("%a, %d %b %Y "
                                                          "%H:%M:%S GMT"),
               'ETag': str(file.md5)}

    #TODO: something nice with etag
       #return HTTPResponse("Not modified", status=304, header=header)

    if bottle.request.method == 'HEAD':
        return bottle.HTTPResponse('', header=headers)
    else:
        return bottle.HTTPResponse(iter(file), header=headers)

if __name__ == '__main__':
    bottle.debug(DEBUG)
    bottle.run(server=SERVER)
