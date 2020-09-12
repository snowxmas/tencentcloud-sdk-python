#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import aiohttp, httpx

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class ApiRequest(object):
    def __init__(self, host, req_timeout=60, debug=False, proxy=None, is_http=False):
        '''
        if is_http:
            self.conn = ProxyHTTPConnection(host, timeout=req_timeout, proxy=proxy)
        else:
            self.conn = ProxyHTTPSConnection(host, timeout=req_timeout, proxy=proxy)
        '''
        self.req_timeout = req_timeout
        self.keep_alive = False
        self.debug = debug
        self.request_size = 0
        self.response_size = 0

    def set_req_timeout(self, req_timeout):
        self.req_timeout = req_timeout

    def is_keep_alive(self):
        return self.keep_alive

    def set_keep_alive(self, flag=True):
        self.keep_alive = flag

    def set_debug(self, debug):
        self.debug = debug

    async def _request(self, req_inter):
        resp = None
        headers_str = dict()
        for k, v in req_inter.header.items():
            if not isinstance( v, str ):
                v = str( v )
            headers_str[k] = v

        if self.debug:
            print("SendRequest %s" % req_inter)
        async with httpx.AsyncClient() as sess:
            if req_inter.method == 'GET':
                req_inter_url = '%s?%s' % (req_inter.uri, req_inter.data)
                resp = await sess.get( f"https://{req_inter.host}{req_inter_url}", headers=headers_str )
            elif req_inter.method == 'POST':
                resp = await sess.post( f"https://{req_inter.host}{req_inter.uri}", data=req_inter.data, headers=headers_str )
            else:
                raise TencentCloudSDKException(
                    "ClientParamsError", 'Method only support (GET, POST)' )
        return resp

    async def send_request(self, req_inter):
        try:
            http_resp = await self._request(req_inter)
            headers = dict(http_resp.headers)
            resp_inter = ResponseInternal(status=http_resp.status_code,
                                          header=headers,
                                          data=http_resp.text)
            # self.request_size = self.conn.request_length
            self.response_size = len(resp_inter.data)
            '''
            if not self.is_keep_alive():
                self.conn.close()
            '''
            if self.debug:
                print(("GetResponse %s" % resp_inter))
            return resp_inter
        except Exception as e:
            self.conn.close()
            raise TencentCloudSDKException("ClientNetworkError", str(e))


class RequestInternal(object):
    def __init__(self, host="", method="", uri="", header=None, data=""):
        if header is None:
            header = {}
        self.host = host
        self.method = method
        self.uri = uri
        self.header = header
        self.data = data

    def __str__(self):
        headers = "\n".join("%s: %s" % (k, v) for k, v in self.header.items())
        return ("Host: %s\nMethod: %s\nUri: %s\nHeader: %s\nData: %s\n"
                % (self.host, self.method, self.uri, headers, self.data))


class ResponseInternal(object):
    def __init__(self, status=0, header=None, data=""):
        if header is None:
            header = {}
        self.status = status
        self.header = header
        self.data = data

    def __str__(self):
        headers = "\n".join("%s: %s" % (k, v) for k, v in self.header.items())
        return ("Status: %s\nHeader: %s\nData: %s\n"
                % (self.status, headers, self.data))
