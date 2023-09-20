from odoo import models
import xlsxwriter, io, base64


class bp_rab_rpt_rab(models.Model):
    _name 	= 'bp_rab.rpt_rab'

    def get_rpt_rab_excel(self, rab):
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet('RAB ' + rab.name)
        format_header_tbl = wb.add_format({'bold':True, 'align':'center', 'valign': 'vcenter', 'font_size': 11, 'bottom':1, 'top':1})
        format_text_left = wb.add_format({'align':'left', 'font_size': 11, 'bottom':1, 'top':1})
        format_text_center = wb.add_format({'align':'center', 'font_size': 11, 'bottom':1, 'top':1})
        format_text_left_bold = wb.add_format({'bold':True, 'align':'left', 'font_size': 11, 'bottom':1, 'top':1})
        format_number_bold = wb.add_format({'bold':True, 'num_format': '#,##0.00','align':'right', 'font_size': 11, 'bottom':1, 'top':1})
        format_number = wb.add_format({'num_format': '#,##0.00','align':'right', 'font_size': 11, 'bottom':1, 'top':1})
        format_border = wb.add_format({'left': 1, 'bottom':1, 'right':1, 'top':1})
        
        ws.set_paper(9)
        ws.set_landscape()
        ws.set_margins(0.5,0.5,0.5,0.5)
        ws.set_column('A:C', 4)
        ws.set_column('D:F', 30)
        ws.set_column('G:J', 7)
        ws.set_column('K:K', 9)
        ws.set_column('L:L', 7)
        ws.set_column('M:M', 9)
        ws.set_column('N:N', 7)
        ws.set_column('O:P', 14)
        ws.set_column('Q:Q', 6)
        
        ws.merge_range('A1:Q1', 'RENCANA ANGGARAN BIAYA', wb.add_format({'bold': True, 'align': 'center', 'font_size': 13}))
        ws.write('A3', 'Customer')
        ws.write('C3', ':', wb.add_format({'align':'center'}))
        ws.write('D3', rab.partner_id.name)
        ws.write('A4', 'Pekerjaan')
        ws.write('C4', ':', wb.add_format({'align':'center'}))
        ws.write('D4', rab.name)
        ws.write('A5', 'Lokasi')
        ws.write('C5', ':', wb.add_format({'align':'center'}))
        ws.write('D5', rab.lokasi if rab.lokasi else '')

        ws.merge_range('A7:C8', 'No', format_header_tbl)
        ws.merge_range('D7:D8', 'Item Pekerjaan', format_header_tbl)
        ws.merge_range('E7:E8', 'Kode Gambar', format_header_tbl)
        ws.merge_range('F7:F8', 'Spesifikasi', format_header_tbl)
        ws.merge_range('G7:J7', 'Volume', format_header_tbl)
        ws.write('G8', 'P', format_header_tbl)
        ws.write('H8', 'L', format_header_tbl)
        ws.write('I8', 'T', format_header_tbl)
        ws.write('J8', 'Unit', format_header_tbl)
        ws.merge_range('K7:K8', 'Vol', format_header_tbl)
        ws.merge_range('L7:L8', 'Idx', format_header_tbl)
        ws.merge_range('M7:M8', 'Vol Akhir', format_header_tbl)
        ws.merge_range('N7:N8', 'Sat', format_header_tbl)
        ws.merge_range('O7:O8', 'HSP', format_header_tbl)
        ws.merge_range('P7:P8', 'Jumlah', format_header_tbl)
        ws.merge_range('Q7:Q8', 'Bobot', format_header_tbl)

        row = 8
        no = 1
        no_group = 1
        no_sub_group = 1
        group = ''
        sub_group = ''
        for i in rab.rab_pekerjaan_ids:
            if not group == i.group_id.name :
                self.excel_insert_group(row, no_group, i.group_id.name, ws, format_header_tbl, format_text_left_bold)
                group = i.group_id.name
                row += 1
                no_group += 1
                no_sub_group = 1
            if not sub_group == i.group_line_id.name:
                self.excel_insert_sub_group(row, no_sub_group, i.group_line_id.name, ws, format_header_tbl, format_text_left_bold)
                sub_group = i.group_line_id.name
                row += 1
                no_sub_group += 1
                no = 1

            ws.write(row, 0, '', format_text_center)
            ws.write(row, 1, '', format_text_center)
            ws.write(row, 2, no, format_text_center)
            ws.write(row, 3, i.name, format_text_left)
            ws.write(row, 4, i.kode_gambar if i.kode_gambar else '', format_text_left)
            ws.write(row, 5, i.spesifikasi if i.spesifikasi else '', format_text_left)
            ws.write(row, 6, i.panjang, format_number)
            ws.write(row, 7, i.lebar, format_number)
            ws.write(row, 8, i.tinggi, format_number)
            ws.write(row, 9, i.unit, format_number)
            ws.write(row, 10, i.volume, format_number)
            ws.write(row, 11, i.index, format_number)
            ws.write(row, 12, i.volume_akhir, format_number)
            ws.write(row, 13, 'm3', format_number)
            ws.write(row, 14, i.hsp, format_number)
            ws.write(row, 15, i.total, format_number)
            ws.write(row, 16, i.bobot, format_number)
            row += 1
            no += 1
        
        ws.merge_range('A' + str(row+1) + ':O' + str(row+1), 'Total', format_header_tbl)
        ws.write(row, 15, rab.total, format_number_bold)
        ws.write(row, 16, '', format_text_center)

        wb.close()
        file_base64 = base64.b64encode(output.getvalue())
        output.close()
        return file_base64
    
    def excel_insert_group(self, row, no, name, ws, format_number, format_text):
        ws.write(row, 0, self.to_roman(no), format_number)
        ws.merge_range('B' + str(row+1) + ':Q' + str(row+1), name, format_text)

    def excel_insert_sub_group(self, row, no, name, ws, format_number, format_text):
        ws.write(row, 0, '', format_number)
        ws.write(row, 1, self.to_letter(no), format_number)
        ws.merge_range('C' + str(row+1) + ':Q' + str(row+1), name, format_text)

    def to_roman(self, num):
        roman_numerals = {100: "C", 90: "XC", 50: "L", 40: "XL", 10: "X", 9: "IX", 5: "V", 4: "IV", 1: "I"}
        result = ""
        for value, numeral in roman_numerals.items():
            while num >= value:
                result += numeral
                num -= value
        
        return result
    
    def to_letter(self, num):
        letters = {
            1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h", 9: "i", 10: "j",
            11: "k", 12: "l", 13: "m", 14: "n", 15: "o", 16: "p", 17: "q", 18: "r", 19: "s", 20: "t",
            21: "u", 22: "v", 23: "w", 24: "x", 25: "y", 26: "z"}

        result = ""
        # Jika angka lebih kecil dari 27
        if num < 27:
            result = letters[num]
        # Jika angka lebih besar dari 26
        else:
            # Menentukan huruf pertama
            first_letter = letters[(num - 1) // 26]
            # Menentukan huruf kedua
            second_letter = letters[num % 26] if num % 26 != 0 else "z"
            result = f"{first_letter}{second_letter}"

        return result.upper()