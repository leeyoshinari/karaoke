#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from tortoise import fields
from tortoise.models import Model
from pydantic import BaseModel


class Files(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    name = fields.CharField(max_length=64, description='文件名')
    is_sing = fields.IntField(default=0, description='歌是否开始唱, 0-不可以, 1-可以')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'files'


class History(Model):
    id = fields.IntField(pk=True, description='主键')
    name = fields.CharField(max_length=64, description='文件名')
    times = fields.IntField(default=0, description='K歌次数')
    is_sing = fields.IntField(default=0, description='歌是否唱过, 0-没唱过, 1-唱过')
    is_top = fields.IntField(default=0, description='是否置顶, 0-不置顶, 1-置顶')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True, index=True)

    class Meta:
        db_table = 'history'


class FileList(BaseModel):
    id: int
    name: str
    is_sing: int
    create_time: str
    update_time: str

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Files):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(id=obj.id, name=obj.name, is_sing=obj.is_sing, create_time=c, update_time=m)


class HistoryList(BaseModel):
    id: int
    name: str
    times: int
    is_sing: int
    is_top: int

    class Config:
        orm_mode = True
        from_attributes = True

    # @classmethod
    # def from_orm_format(cls, obj: History):
    #     c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
    #     m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
    #     return cls(id=obj.id, name=obj.name, times=obj.times, create_time=c, update_time=m)
