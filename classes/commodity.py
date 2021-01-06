import sys
import os


class Commodity:
    def __init__(self, goods_nomenclature_sid, goods_nomenclature_item_id, productline_suffix, description):
        self.goods_nomenclature_sid = goods_nomenclature_sid
        self.goods_nomenclature_item_id = goods_nomenclature_item_id
        self.productline_suffix = productline_suffix
        self.description = description
        self.combined_code = self.goods_nomenclature_item_id + self.productline_suffix
        self.combined = self.goods_nomenclature_item_id + self.productline_suffix + self.description
        self.validity_start_date = None
        self.validity_end_date = None
        pass
