# -- coding: utf-8 --
from enum import unique, Enum


class WpsDriverPort(object):
    """
    定义请求路径
    """
    port_dict = {'PROME': '2020', 'WPS': '2021', 'ET': '2022', 'WPP': '2023', 'PDF': '2024', 'WPS_INSTANCE_ONE': '2030',
                 'WPS_INSTANCE_TWO': '2031', 'WPS_INSTANCE_THREE': '2032'}


@unique
class AppType(Enum):
    PROME = "PROME"
    WPS = "WPS"
    ET = "ET"
    WPP = "WPP"
    PDF = "PDF"
    WPS_INSTANCE_ONE = 'WPS_INSTANCE_ONE'
    WPS_INSTANCE_TWO = 'WPS_INSTANCE_TWO'
    WPS_INSTANCE_THREE = 'WPS_INSTANCE_THREE'
