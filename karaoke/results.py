#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

class Result:
    def __init__(self, code=0, msg='Success!', data=None, total=0, page=0, total_page=0):
        self.code = code
        self.msg = msg
        self.data = data
        self.total = total
        self.page = page
        self.totalPage = total_page
