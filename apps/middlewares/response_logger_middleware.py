
from flask import Flask, request

class ResponseLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, environ, start_response):
        request_data = await self._read_request_data(environ)
        self._log_request_info(environ, request_data)

        def custom_start_response(status, headers, exc_info=None):
            response = start_response(status, headers, exc_info)
            self._log_response_info(status, headers)
            return response
        
        return await self.app(environ, custom_start_response)
    
    async def _read_request_data(self, environ):
        if environ['REQUEST_METHOD'] in ['POST', 'PUT', 'PATCH']:
            content_length = int(environ.get('CONTENT_LENGTH') or 0)
            return await request.stream.read(content_length)
        return None
    
    def _log_request_info(self, environ, request_data):
        self.app.logger.debug()