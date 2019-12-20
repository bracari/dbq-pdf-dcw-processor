import xml.etree.ElementTree as ET
from operator import attrgetter, methodcaller

from dcwTranslator import SimpleTranslator, simpleCheckBoxBinder, simpleTextBinder
from orderedElement import OrderedElement, Section, Question, LabelType, FieldType, DTAQuestion

import xlsxwriter
import math

tree = ET.parse("neuro-headache-pdf.xml")
root = tree.getroot()

field_names = {}
fields = {}

drawing_names = {}
drawings = {}
page_lines = {}

count = 0
page_elements = {}

pages = root.findall(".//t:template/t:subform/t:subform", OrderedElement.ns) #+ root.findall(".//t:template/t:subform/t:subform/t:subform", ns)

#Parse sections from pages
sections = {}
for page in pages:
    if count == 0:
        count += 1
        continue
    page_name = "Page{}".format(count)
    page_elements.update({page_name: []})
    page_lines.update({page_name: []})

    sections.update({page_name: []})

    for draw_element in page.findall(".//t:draw", OrderedElement.ns):
        ordered_draw = OrderedElement(draw_element)
        if ordered_draw.description is None: continue
        if "SECTION" in ordered_draw.description.upper() and "?" not in ordered_draw.description.upper():
            section = Section(ordered_draw)
            sections[page_name].append(section)
        else:
            page_elements[page_name].append(ordered_draw)

    for line in page.findall(".//t:draw/t:value/t:line/../..", OrderedElement.ns):
        page_lines[page_name].append(OrderedElement(line))

    for field in page.findall(".//t:field", OrderedElement.ns):
        page_elements[page_name].append(OrderedElement(field))
    count += 1


#Pre-Order sections and set bounds
for page in sections:
    prev_section = None
    for section in sorted(sections[page], key=attrgetter('header.y')):
        if prev_section is not None:
            prev_section.lower = section.upper
        prev_section = section

#Parse questions
questions = {}
for page in sections:
    question = None
    count = 0
    for section in sorted(sections[page], key=attrgetter('header.y')):
        line_count = 0
        for line in sorted(page_lines[page], key=attrgetter('y')):
            if section.upper > line.y:
                continue
            if section.lower < line.y:
                break

            y_str = "{}mm".format(line.y)
            h_str = "{}mm".format(line.h)
            if line_count == 0:
                question = Question(y_str, '9999mm')
                section.questions.append(question)
            else:
                question.set_lower_bound(y_str, h_str)

                for element in sorted(page_elements[page], key=attrgetter('y')):
                    if int(question.upper) > int(element.y):
                        continue
                    if int(question.lower) <= int(element.y):
                        break
                    question.add_element(element)

                question = Question(y_str, '9999mm')
                section.questions.append(question)
            line_count += 1

        # if question is not None:
        #     question.set_lower_bound(y_str, h_str)
        #
        #     for element in sorted(page_elements[page], key=attrgetter('y')):
        #         if int(question.upper) > int(element.y):
        #             continue
        #         if int(question.lower) <= int(element.y):
        #             break
        #         question.add_element(element)
        #
        #     question = Question(y_str, '9999mm')
        #     section.questions.append(question)

        count += 1


for page in sections:
    for section in sorted(sections[page], key=attrgetter('header.y')):
        for question in sorted(section.questions, key=attrgetter('lower')):
            if len(question.elements) == 0: continue
            translator = SimpleTranslator(question)
            question_labels = translator.get_ordered_labels(LabelType.QUESTION_LABEL) + translator.get_ordered_labels(LabelType.CONDITION_LABEL)
            dta_question = None
            dta_count = 0
            for question_label in sorted(question_labels, key=attrgetter('y')):
                y_str = "{}mm".format(question_label.y)
                h_str = "{}mm".format(question_label.h)
                if dta_count == 0:
                    dta_question = DTAQuestion(y_str, '9999mm', question_label)
                    section.dta_questions.append(dta_question)
                else:
                    dta_question.set_lower_bound(y_str, h_str)

                    fields = translator.get_ordered_fields(FieldType.ALPHA)
                    binder = simpleCheckBoxBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
                    dta_question.mapper(binder)

                    fields = translator.get_ordered_fields(FieldType.FREE_TEXT) + translator.get_ordered_fields(
                        FieldType.DATE)
                    binder = simpleTextBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
                    dta_question.mapper(binder)

                    fields = translator.get_ordered_fields(FieldType.RICH_TEXT)
                    dta_question.mapper(binder)

                    dta_question = DTAQuestion(y_str, '9999mm', question_label)
                    section.dta_questions.append(dta_question)

                dta_count += 1
            if dta_question is not None and dta_question.lower == float(9999):
                y_str = "{}mm".format(question.lower)
                h_str = "{}mm".format(question.lower)
                dta_question.set_lower_bound(y_str, h_str)

                fields = translator.get_ordered_fields(FieldType.ALPHA)
                binder = simpleCheckBoxBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
                dta_question.mapper(binder)

                fields = translator.get_ordered_fields(FieldType.FREE_TEXT) + translator.get_ordered_fields(
                    FieldType.DATE)
                binder = simpleTextBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
                dta_question.mapper(binder)

                fields = translator.get_ordered_fields(FieldType.RICH_TEXT)
                if len(fields) > 0:
                    dta_question.dta_elements.update({'None': [FieldType.RICH_TEXT]})

            # y_str = "{}mm".format(question.lower)
            # h_str = "{}mm".format(question.lower)
            # dta_question.set_lower_bound(y_str, h_str)
            #
            # fields = translator.get_ordered_fields(FieldType.ALPHA)
            # binder = simpleCheckBoxBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
            # dta_question.mapper(binder)
            #
            # fields = translator.get_ordered_fields(FieldType.FREE_TEXT) + translator.get_ordered_fields(
            #     FieldType.DATE)
            # binder = simpleTextBinder(fields, translator.get_ordered_labels(LabelType.DTA_LABEL))
            # dta_question.mapper(binder)
            #
            # fields = translator.get_ordered_fields(FieldType.RICH_TEXT)
            # dta_question.mapper(binder)

count = 1
for page in sections:
    print(page)
    for section in sorted(sections[page], key=attrgetter('header.y')):
        print("\t{} at y={}".format(section.header.description, section.header.y))
        for question in sorted(section.dta_questions, key=attrgetter('lower')):
            print("\t\tQuestion:{}".format(question.label.description))

            for dta in question.dta_elements:
                print("\t\t\t{}{}".format(dta, question.dta_elements[dta]))
