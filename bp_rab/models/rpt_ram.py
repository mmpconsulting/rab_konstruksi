from odoo import models
import xlsxwriter, io, base64


class bp_rab_rpt_ram(models.Model):
    _name 	= 'bp_rab.rpt_ram'

    def get_rpt_ram_excel(self, rab, data, rpt_name):
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet(rpt_name + ' ' + rab.name)
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
        ws.set_column('A:B', 5)
        ws.set_column('C:C', 2)
        ws.set_column('D:E', 30)
        ws.set_column('F:G', 10)
        ws.set_column('H:I', 17)
        
        ws.merge_range('A1:I1', 'RENCANA ANGGARAN MATERIAL' if rpt_name == 'RAM' else 'RENCANA ANGGARAN JASA', wb.add_format({'bold': True, 'align': 'center', 'font_size': 13}))
        ws.write('A3', 'Customer')
        ws.write('C3', ':', wb.add_format({'align':'center'}))
        ws.write('D3', rab.partner_id.name)
        ws.write('A4', 'Pekerjaan')
        ws.write('C4', ':', wb.add_format({'align':'center'}))
        ws.write('D4', rab.name)
        ws.write('A5', 'Lokasi')
        ws.write('C5', ':', wb.add_format({'align':'center'}))
        ws.write('D5', rab.lokasi if rab.lokasi else '')

        ws.write('A7', 'No', format_header_tbl)
        ws.merge_range('B7:D7', 'List Material' if rpt_name == 'RAM' else 'List Jasa', format_header_tbl)
        ws.write('E7', 'List Item Pekerjaan', format_header_tbl)
        ws.write('F7', 'Qty', format_header_tbl)
        ws.write('G7', 'Uom', format_header_tbl)
        ws.write('H7', 'Price', format_header_tbl)
        ws.write('I7', 'Total', format_header_tbl)

        row = 7
        no = 1
        for i in data:
            ws.write(row, 0, no, format_text_center)
            ws.merge_range('B' + str(row+1) + ':D' + str(row+1), i.product_id.name, format_text_left)
            ws.write(row, 4, '', format_text_left)
            ws.write(row, 5, i.qty, format_number)
            ws.write(row, 6, i.product_id.uom_id.name, format_text_center)
            ws.write(row, 7, i.price, format_number)
            ws.write(row, 8, i.total, format_number)
            row += 1
            no += 1
            for j in i.rab_formula_line_ids:
                ws.write(row, 0, '', format_text_center)
                ws.merge_range('B' + str(row+1) + ':D' + str(row+1), '', format_text_left)
                ws.write(row, 4, j.rab_pekerjaan_id.name, format_text_left)
                ws.write(row, 5, j.qty, format_number)
                ws.write(row, 6, '', format_text_center)
                ws.write(row, 7, '', format_text_center)
                ws.write(row, 8, '', format_text_center)
                row += 1

        
        wb.close()
        file_base64 = base64.b64encode(output.getvalue())
        output.close()
        return file_base64
    