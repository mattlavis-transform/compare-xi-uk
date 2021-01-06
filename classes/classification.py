import csv
import sys
import os
from .database import Database
from .commodity import Commodity


def m_str(s):
    if s is None:
        return ""
    else:
        return str(s)


class Classification:
    def __init__(self, which):
        self.which = which

    def run(self):
        cwd = os.getcwd()
        subfolder = os.path.join(cwd, "export")
        subfolder = os.path.join(subfolder, self.which)

        for item in range(0, 10):
            print("Recording commodities beginning with", str(
                item), "for", self.which.upper(), "tariff")
            item = str(item)
            filename = os.path.join(subfolder, item + ".csv")
            f = open(filename, "w+")
            sql = """select goods_nomenclature_sid, goods_nomenclature_item_id, producline_suffix, description
            from utils.goods_nomenclature_export_new('""" + str(item) + """%', '2021-01-04')
            order by 2, 3;"""
            d = Database(self.which)
            d.open_connection()
            rows = d.run_query(sql)
            f.write(
                'goods_nomenclature_sid,goods_nomenclature_item_id,productline_suffix,description\n')
            for row in rows:
                goods_nomenclature_sid = row[0]
                goods_nomenclature_item_id = row[1]
                productline_suffix = row[2]
                if row[3] is None:
                    description = ""
                else:
                    description = row[3]
                    description = description.replace('"', "")
                    description = description.replace(",", "")
                    description = description.replace("|", " ")

                f.write(str(goods_nomenclature_sid) + ',"' + goods_nomenclature_item_id + '","' +
                        productline_suffix + '","' + description + '"' + "\n")
            f.close()

    def compare(self):
        # Then load and compare
        tariffs = ["uk", "xi"]
        cwd = os.getcwd()
        subfolder = os.path.join(cwd, "export")
        new_dict = {}
        print("Reading XI and UK tariffs")
        for tariff in tariffs:
            code_list = []
            for item in range(0, 10):
                item = str(item)
                subfolder2 = os.path.join(subfolder, tariff)
                filename = os.path.join(subfolder2, item + ".csv")
                with open(filename, mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        try:
                            c = Commodity(
                                row["goods_nomenclature_sid"], row["goods_nomenclature_item_id"], row["productline_suffix"], row["description"])
                            code_list.append(c)
                        except:
                            pass
            new_dict[tariff] = code_list

        uk_tariff = new_dict["uk"]
        xi_tariff = new_dict["xi"]

        uk_only = []
        xi_only = []
        max_increment = 100

        print("Comparing XI and UK tariffs - looking for UK only")
        xi_tariff_count = len(xi_tariff)
        uk_sid_list = ""
        minimum = 0
        for code_uk in uk_tariff:
            found = False
            maximum = min(minimum + max_increment, xi_tariff_count)
            for i in range(minimum, maximum):
                code_xi = xi_tariff[i]
                if code_uk.combined_code == code_xi.combined_code:
                    found = True
                    minimum = min(i, xi_tariff_count)
                    break

            if found == False:
                uk_only.append(code_uk)
                uk_sid_list += str(code_uk.goods_nomenclature_sid) + ", "

        print("Comparing XI and UK tariffs - looking for XI only")
        uk_tariff_count = len(uk_tariff)
        xi_sid_list = ""
        minimum = 0
        for code_xi in xi_tariff:
            found = False
            maximum = min(minimum + max_increment, uk_tariff_count)
            for i in range(minimum, maximum):
                code_uk = uk_tariff[i]
                if code_xi.combined_code == code_uk.combined_code:
                    found = True
                    minimum = min(i, uk_tariff_count)
                    break

            if found == False:
                xi_only.append(code_xi)
                xi_sid_list += str(code_xi.goods_nomenclature_sid) + ", "

        # Check for end dates in the XI database for the EU only commodities
        uk_sid_list = uk_sid_list.strip()
        uk_sid_list = uk_sid_list.strip(",")
        sql = """select goods_nomenclature_sid, goods_nomenclature_item_id, producline_suffix, validity_end_date
            from goods_nomenclatures where goods_nomenclature_sid in (""" + uk_sid_list + """)
            order by 1;"""
        d = Database("xi")
        rows = d.run_query(sql)
        xi_comms = []
        for row in rows:
            c = Commodity(row[0], row[1], row[2], "")
            c.validity_end_date = row[3]
            xi_comms.append(c)
        a = 1

        for uk_item in uk_only:
            for xi_item in xi_comms:
                if str(uk_item.goods_nomenclature_sid) == str(xi_item.goods_nomenclature_sid):
                    uk_item.validity_end_date = xi_item.validity_end_date
                    break

        # Check for start dates in the XI database for the EU only commodities
        xi_sid_list = xi_sid_list.strip()
        xi_sid_list = xi_sid_list.strip(",")
        sql = """select goods_nomenclature_sid, goods_nomenclature_item_id, producline_suffix, validity_start_date
            from goods_nomenclatures where goods_nomenclature_sid in (""" + xi_sid_list + """)
            order by 1;"""
        d = Database("xi")
        rows = d.run_query(sql)
        xi_comms = []
        for row in rows:
            c = Commodity(row[0], row[1], row[2], "")
            c.validity_start_date = row[3]
            xi_comms.append(c)
        a = 1

        for item in xi_only:
            for xi_item in xi_comms:
                if str(item.goods_nomenclature_sid) == str(xi_item.goods_nomenclature_sid):
                    item.validity_start_date = xi_item.validity_start_date
                    break

        print("Writing difference files")
        filename = os.path.join(subfolder, "uk_only.csv")
        f = open(filename, "w")
        f.write(
            'goods_nomenclature_sid,goods_nomenclature_item_id,productline_suffix,description, XI(EU) end date\n')
        for code_uk in uk_only:
            f.write(code_uk.goods_nomenclature_sid + ',"' + code_uk.goods_nomenclature_item_id + '","' +
                    code_uk.productline_suffix + '","' + code_uk.description + '","' + m_str(code_uk.validity_end_date) + '"' + "\n")
        f.close()

        filename = os.path.join(subfolder, "xi_only.csv")
        f = open(filename, "w")
        f.write(
            'goods_nomenclature_sid,goods_nomenclature_item_id,productline_suffix,description, XI(EU) start date\n')
        for code_xi in xi_only:
            f.write(code_xi.goods_nomenclature_sid + ',"' + code_xi.goods_nomenclature_item_id + '","' +
                    code_xi.productline_suffix + '","' + code_xi.description + '","' + m_str(code_xi.validity_start_date) + '"' + "\n")
        f.close()
