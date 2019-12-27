from collections import Counter

import xlsxwriter

from orderedElement import FieldType


def element_transformer(dta_elements):
    field_types = {FieldType.ALPHA: 'Alpha',
                   FieldType.RICH_TEXT: 'Rich Text',
                   FieldType.FREE_TEXT: 'Free Text'}

    type = None
    alpha_responses = []

    if len(dta_elements) == 0:
        return type, alpha_responses
    if len(dta_elements) == 1:
        for dta in dta_elements:
            type = field_types[dta_elements[dta][0]]
        return type, alpha_responses

    compressed_types = []
    for label in dta_elements:
        compressed_types.extend(dta_elements[label])
        alpha_responses.append(label)

    type_count = Counter(compressed_types)

    if len(type_count) == 1 and 'YES' in dta_elements:
        type = 'Alpha'
    elif len(type_count) == 1:
        type = 'Multi-alpha'
    elif len(type_count) >= 2:
        type = 'Multi-alpha and Freetext'

    return type, alpha_responses

class Logger:
    OUTBOUND_PATH = 'logging/'

    def write_row(self, dta_question, bound_element, upper_collision, lower_collision):
        self.worksheet.write(self.curr_row, 1, dta_question.label.description)
        self.worksheet.write(self.curr_row, 2, dta_question.upper)
        self.worksheet.write(self.curr_row, 3, dta_question.left)
        self.worksheet.write(self.curr_row, 4, dta_question.lower)
        self.worksheet.write(self.curr_row, 5, dta_question.right)
        self.worksheet.write(self.curr_row, 6, bound_element.name)
        self.worksheet.write(self.curr_row, 7, bound_element.x)
        self.worksheet.write(self.curr_row, 8, bound_element.y)
        self.worksheet.write(self.curr_row, 9, upper_collision)
        self.worksheet.write(self.curr_row, 10, lower_collision)

        self.curr_row += 1

    def commit(self):
        self.workbook.close()

    def __init__(self, xlsx_output_filename):
        self.workbook = xlsxwriter.Workbook(Logger.OUTBOUND_PATH + xlsx_output_filename)
        self.worksheet = self.workbook.add_worksheet('Log')

        sub_header = ( 'Label', 'Upper', 'Left', 'Lower', 'Right', 'Element Name', 'Element X', 'Element Y', 'Upper Collision', 'Lower Collision')

        sub_header_format = self.workbook.add_format()
        sub_header_format.set_bg_color('#CCFFCC')
        sub_header_format.set_font_color('black')
        sub_header_format.set_font('Arial')
        sub_header_format.set_bold(True)
        sub_header_format.set_font_size(8)
        sub_header_format.set_border(1)
        self.worksheet.write_row(0, 0, sub_header, sub_header_format)

        self.curr_row = 1


class PowerFormDCWWriter:
    OUTBOUND_PATH = 'outbound/'

    def write_section_row(self, section):
        self.worksheet.write(self.curr_row, 3, 'New', self.word_wrap)
        self.worksheet.write(self.curr_row, 4, 'Section', self.word_wrap)
        self.worksheet.write(self.curr_row, 5, section.ordinal_str, self.word_wrap)
        self.worksheet.write(self.curr_row, 6, section.header.description, self.word_wrap)
        self.worksheet.write(self.curr_row, 7, section.header.description, self.word_wrap)
        self.worksheet.write(self.curr_row, 8, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 9, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 10, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 11, None, self.word_wrap)

        self.curr_row += 1


    def write_banner_row(self, section):
        self.worksheet.write(self.curr_row, 3, 'New', self.word_wrap)
        self.worksheet.write(self.curr_row, 4, 'Banner', self.word_wrap)
        self.worksheet.write(self.curr_row, 5, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 6, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 7, None, self.word_wrap)

        parsed_banner = section.header.description.split('-')[1]
        self.worksheet.write(self.curr_row, 8, parsed_banner.strip(), self.word_wrap)
        self.worksheet.write(self.curr_row, 9, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 10, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 11, None, self.word_wrap)

        self.curr_row += 1


    def write_label_row(self, dta_question):
        self.worksheet.write(self.curr_row, 3, 'New', self.word_wrap)
        self.worksheet.write(self.curr_row, 4, 'Label', self.word_wrap)
        self.worksheet.write(self.curr_row, 5, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 6, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 7, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 8, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 9, dta_question.label.description, self.word_wrap)
        self.worksheet.write(self.curr_row, 10, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 11, None, self.word_wrap)

        self.curr_row += 1


    def write_dta_row(self, dta_question):
        self.worksheet.write(self.curr_row, 3, 'New', self.word_wrap)
        self.worksheet.write(self.curr_row, 4, 'DTA', self.word_wrap)
        self.worksheet.write(self.curr_row, 5, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 6, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 7, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 8, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 9, None, self.word_wrap)
        self.worksheet.write(self.curr_row, 10, dta_question.mnemonic, self.word_wrap)

        type, alpha_responses = element_transformer(dta_question.dta_elements)
        self.worksheet.write(self.curr_row, 11, type, self.word_wrap)

        self.curr_row += 1

    def commit(self):
        self.workbook.close()

    def __init__(self, xlsx_output_filename):
        self.workbook = xlsxwriter.Workbook(PowerFormDCWWriter.OUTBOUND_PATH + xlsx_output_filename)
        self.worksheet = self.workbook.add_worksheet('Test')

        # Common format for word wrap
        self.word_wrap = self.workbook.add_format()
        self.word_wrap.set_bg_color('#92D050')
        self.word_wrap.set_font('Calibri')
        self.word_wrap.set_font_size(11)
        self.word_wrap.set_text_wrap()

        # Define Main Header Format
        title_format = self.workbook.add_format()
        title_format.set_bg_color('#DBDBDB')
        title_format.set_font_color('black')
        title_format.set_font('Arial')
        title_format.set_bold(True)
        title_format.set_font_size(8)
        title_format.set_border(1)
        self.worksheet.merge_range('A1:C1', 'Configuration Center', title_format)
        self.worksheet.merge_range('D1:F1', 'Define Modification Info', title_format)
        self.worksheet.merge_range('G1:J1', 'Section Info & Formatting', title_format)
        self.worksheet.merge_range('K1:O1', 'DTA Info', title_format)

        sub_header = ( 'Test Status', 'Build Status', 'Notes',
        'Modification Type', 'Define DetailElement>Name', 'Location Description', 'Section Name', 'Section Display',
        'Banner Bar', 'Label', 'DTA Mnemonic', 'DTA Result Type', 'Req.', '1st Alpha Single Select', 'OtherDefaults',
        'Alpha Responses', 'Conditionality')

        sub_header_format = self.workbook.add_format()
        sub_header_format.set_bg_color('#CCFFCC')
        sub_header_format.set_font_color('black')
        sub_header_format.set_font('Arial')
        sub_header_format.set_bold(True)
        sub_header_format.set_font_size(8)
        sub_header_format.set_border(1)
        self.worksheet.write_row(1, 0, sub_header, sub_header_format)

        # self.worksheet.set_column(0, 0, None, {'hidden': True})
        # self.worksheet.set_column(1, 1, None, {'hidden': True})
        # self.worksheet.set_column(2, 2, None, {'hidden': True})
        self.worksheet.set_column(3, 3, 8.54)
        self.worksheet.set_column(4, 4, 8.54)
        self.worksheet.set_column(5, 5, 13.85)
        self.worksheet.set_column(6, 6, 17.08)
        self.worksheet.set_column(7, 7, 17.08)
        self.worksheet.set_column(8, 8, 25.08)
        self.worksheet.set_column(9, 9, 109.31)
        self.worksheet.set_column(10, 10, 50.08)
        self.worksheet.set_column(11, 11, 20.62)

        self.curr_row = 2


class AuditDCWWriter:
    OUTBOUND_PATH = 'outbound/'

    def write_row(self, dta_question):
        mnemonic = dta_question.mnemonic
        description = dta_question.label.description
        activity_type = 'Patient Care'

        self.worksheet.write(self.curr_row, 1, mnemonic, self.word_wrap)
        self.worksheet.write(self.curr_row, 2, description, self.word_wrap)
        self.worksheet.write(self.curr_row, 4, 'Patient Care')

        type, alpha_responses = element_transformer(dta_question.dta_elements)
        self.worksheet.write(self.curr_row, 5, type)

        for alpha in alpha_responses:
            self.worksheet.write(self.curr_row, 6, alpha)
            self.curr_row += 1

        self.curr_row += 1

    def commit(self):
        self.workbook.close()

    def __init__(self, xlsx_output_filename):
        self.workbook = xlsxwriter.Workbook(AuditDCWWriter.OUTBOUND_PATH + xlsx_output_filename)
        self.worksheet = self.workbook.add_worksheet('Test')

        # Common format for word wrap
        self.word_wrap = self.workbook.add_format()
        self.word_wrap.set_text_wrap()

        # Define Main Header Format
        title_format = self.workbook.add_format()
        title_format.set_bg_color('#0F6EB4')
        title_format.set_font_color('white')
        title_format.set_font('Segoe UI Light')
        title_format.set_font_size(22)
        self.worksheet.merge_range('A1:BJ1', 'All DTAs - Audit', title_format)

        sub_header = (
            'Action', 'Mnemonic', 'Description', 'Task Assay CD', 'Activity Type', 'Result Type', 'Alpha Response',
            'Alpha Sequence', 'Alpha Result Value', 'Alpha Concept CKI', 'Alpha Truth State', 'Alpha Grid Display',
            'Alpha Default', 'Alpha Source Vocabulary', 'Alpha Principle Type', 'Alpha Vocab Axis',
            'Alpha Contrib System',
            'Alpha Language', 'Numeric Max', 'Numeric Min', 'Numeric Decimal', 'Use Modifier', 'First Alpha Single',
            'Witness Required', 'Code Set', 'Event CD', 'Event CD Display', 'Concept CKI', 'Default Type',
            'Default Template', 'Intake and Output', 'Look Back Minutes for Results', 'Look Back Minutes for BMDI',
            'Look Forward Minutes for BMDI', 'Sex', 'Age Range', 'Minutes Back', 'Normal Low', 'Normal High',
            'Feasible Low', 'Feasible High', 'Linear Low', 'Linear High', 'Critical Low', 'Critical High', 'Review Low',
            'Review High', 'Default Result', 'Units of Measure', 'Alpha Category Name', 'Alpha Category Sequence',
            'Alpha Category Expand Flag', 'Errors', 'Calculation', 'Location', 'PowerForms', 'Iviews',
            'Outcomes/Interventions', 'ActivityViews', 'DynamicGrpLabel', 'DynamicGrpTemp', 'MarCharting')

        sub_header_format = self.workbook.add_format()
        sub_header_format.set_bg_color('#48545D')
        sub_header_format.set_font_color('white')
        sub_header_format.set_font('Segoe UI')
        sub_header_format.set_bold(True)
        sub_header_format.set_font_size(9)
        self.worksheet.write_row(1, 0, sub_header, sub_header_format)

        self.worksheet.set_column(0, 0, 2)
        self.worksheet.set_column(1, 1, 47)
        self.worksheet.set_column(2, 2, 47)
        self.worksheet.set_column(3, 3, 5)
        self.worksheet.set_column(4, 4, 11)
        self.worksheet.set_column(5, 5, 22)
        self.worksheet.set_column(6, 6, 32)

        self.curr_row = 2
