import xml.etree.ElementTree as ET
from operator import methodcaller, attrgetter

import xlsxwriter
import math
from enum import Enum, IntEnum

ns = {'xdp': 'http://ns.adobe.com/xdp/',
      't': 'http://www.xfa.org/schema/xfa-template/2.8/',
      'xmlns': 'http://www.w3.org/1999/xhtml'}

class Type(Enum):
    HEADER = 1
    LABEL = 2
    CONDITION_LABEL = 3
    DTA = 4

class FieldType(Enum):
    ALPHA = 1
    MULTI_ALPHA = 2
    FREE_TEXT = 4
    RICH_TEXT = 8
    NUMERIC = 16


class Ordered_Element:
    def order(self):
        return math.ceil(self.y / 7) * 1000 + self.x

    def __init__(self, x_str, y_str, name, description, element):
        if isinstance(x_str, float):
            self.x = x_str
        else:
            self.x = float(x_str[:-2])

        if isinstance(y_str, float):
            self.y = y_str
        else:
            self.y = float(y_str[:-2])

        self.name = name
        self.description = description
        self.element = element
        self.element_type = None
        self.type = None
        self.field_type = None


        tag = element.tag
        if tag[-4:] == 'draw' and description is not None:
            if "IF" in description.upper():
                self.type = Type.CONDITION_LABEL
            elif "SECTION" in description.upper():
                self.type = Type.HEADER
            elif "?" in description or "DESCRIBE" in description.upper() or "INDICATE" in description.upper():
                self.type = Type.LABEL
            else:
                self.type = Type.DTA

        else:
            self.type = Type.DTA
            checkbox = element.find("t:ui/t:checkButton", ns)
            textbox = element.find("t:ui/t:textEdit", ns)
            if checkbox is not None:
                self.field_type = FieldType.ALPHA
            if textbox is not None:
                h_str = element.attrib['h'] if 'h' in element.attrib else '1mm'
                h = float(h_str[:-2])
                if h > 5:
                    self.field_type = FieldType.RICH_TEXT
                else:
                    self.field_type = FieldType.FREE_TEXT


class Question:
    def add_element(self, ordered_element: Ordered_Element):
        relative_y = ordered_element.y - self.upper
        #relative_y = ordered_element.y
        org_x = ordered_element.x
        org_name = ordered_element.name
        org_description = ordered_element.description
        org_element = ordered_element.element
        self.elements.append(Ordered_Element(org_x, relative_y, org_name, org_description, org_element))

    def get_elements(self):
        return sorted(self.elements, key=methodcaller('order'))

    def set_lower_bound(self, lower_bound: str, height: str):
        self.lower = float(lower_bound[:-2])
        if self.lower == 9999:
            self.lower = self.upper + float(height[:-2])

    def __init__(self, upper_bound, lower_bound):
        if isinstance(upper_bound, float):
            self.upper = upper_bound
        else:
            self.upper = float(upper_bound[:-2])

        if isinstance(lower_bound, float):
            self.lower = lower_bound
        else:
            self.lower = float(lower_bound[:-2])

        self.elements = []


tree = ET.parse("neuro-headache-pdf.xml")
root = tree.getroot()

field_names = {}
fields = {}

drawing_names = {}
drawings = {}
lines = {}

count = 0
page_group = {}

pages = root.findall(".//t:template/t:subform/t:subform", ns) + root.findall(".//t:template/t:subform/t:subform/t:subform", ns)

for page in pages:
    if count == 0:
        count += 1
        continue
    page_name = "Page{}".format(count)
    page_group.update({page_name: []})
    lines.update({page_name: []})

    for line in page.findall(".//t:draw/t:value/t:line/../..", ns):
        name = line.attrib['name'] if 'name' in line.attrib else None
        if name is None:
            continue
        x_str = line.attrib['x'] if 'x' in line.attrib else '9999mm'
        y_str = line.attrib['y'] if 'y' in line.attrib else '9999mm'
        description = None
        lines[page_name].append(Ordered_Element(x_str, y_str, name, description, line))

    for field in page.findall("t:field", ns):
        name = field.attrib['name'] if 'name' in field.attrib else None
        if name is None:
            continue

        x_str = field.attrib['x'] if 'x' in field.attrib else '9999mm'
        y_str = field.attrib['y'] if 'y' in field.attrib else '9999mm'
        description = None
        page_group[page_name].append(Ordered_Element(x_str, y_str, name, description, field))
        # if name not in field_names:
        #     field_count = 0
        #     field_array = "{}[{}]".format(name, field_count)
        #     fields.update({field_array: field})
        #     field_names.update({name: field_count + 1})
        # else:
        #     field_count = field_names[name]
        #     field_array = "{}[{}]".format(name, field_count)
        #     fields.update({field_array: field})
        #     field_names[name] = field_count + 1

    for draw in page.findall("t:draw", ns):
        name = draw.attrib['name'] if 'name' in draw.attrib else None
        if name is None:
            continue

        text_element = draw.find(".//t:value/t:text", ns)
        formatted_text_element = draw.find(".//t:value/t:exData", ns)
        if text_element is None and formatted_text_element is None:
            continue

        x_str = draw.attrib['x'] if 'x' in draw.attrib else '9999mm'
        y_str = draw.attrib['y'] if 'y' in draw.attrib else '9999mm'

        description = None
        if text_element is not None:
            description = text_element.text
        if formatted_text_element is not None:
            content = []
            for para in formatted_text_element.findall(".//xmlns:body/xmlns:p", ns):
                content.append(para.text.strip())
            for para in formatted_text_element.findall(".//xmlns:body/xmlns:p/xmlns:span", ns):
                content.append(para.text.strip())
            description = "".join(content)

        page_group[page_name].append(Ordered_Element(x_str, y_str, name, description, draw))

        # if name not in drawing_names:
        #     drawing_count = 0
        #     drawing_array = "{}[{}]".format(name, drawing_count)
        #     drawings.update({drawing_array: draw})
        #     drawing_names.update({name: drawing_count + 1})
        # else:
        #     drawing_count = drawing_names[name]
        #     drawing_array = "{}[{}]".format(name, drawing_count)
        #     drawings.update({drawing_array: draw})
        #     drawing_names[name] = drawing_count + 1

    count += 1

questions = {}
for page in lines:
    questions.update({page: []})
    question = None
    count = 0
    for line in sorted(lines[page], key=attrgetter('y')):
        if count == 0:
            y_str = line.element.attrib['y'] if 'y' in line.element.attrib else '9999mm'
            question = Question(y_str, '9999mm')
            questions[page].append(question)
        else:
            y_str = line.element.attrib['y'] if 'y' in line.element.attrib else '9999mm'
            h_str = line.element.attrib['h'] if 'h' in line.element.attrib else '1mm'
            question.set_lower_bound(y_str, h_str)

            for element in sorted(page_group[page], key=attrgetter('y')):
                if int(question.upper) > int(element.y):
                    continue
                if int(question.lower) <= int(element.y):
                    break
                question.add_element(element)

            question = Question(y_str, '9999mm')
            questions[page].append(question)

        count += 1

for page in questions:
    print(page)
    count = 1
    for question in sorted(questions[page], key=attrgetter('lower')):
        print("\tQuestion{} upper:{},lower{}".format(count, question.upper, question.lower))
        for element in question.get_elements():
            print("\t\t{}-{} {}:{} located at y:{}, x:{}".format(element.type, element.field_type, element.name, element.description, element.y, element.x))
        count += 1

    # for key in page_group:
    #     print(key)
    #     for value in sorted(page_group[key], key=methodcaller('order')):
    #         tag = value.element.tag
    #         if tag[-4:] == 'draw':
    #             text_element = value.element.find(".//t:value/t:text", ns)
    #             formatted_text_element = value.element.find(".//t:value/t:exData", ns)
    #
    #             description = None
    #             if text_element is not None:
    #                 description = text_element.text
    #             if formatted_text_element is not None:
    #                 content = []
    #                 for para in formatted_text_element.findall(".//xmlns:body/xmlns:p", ns):
    #                     content.append(para.text.strip())
    #                 for para in formatted_text_element.findall(".//xmlns:body/xmlns:p/xmlns:span", ns):
    #                     content.append(para.text.strip())
    #                 description = "".join(content)
    #             print("\t\t{}:{}:{} \n\t\t\tof x:{} and y:{}".format(value.name, description, value.order(), value.x, value.y))
    #         else:
    #             print("\t\t{}:{} of x:{} and y:{}".format(value.name, value.order(), value.x, value.y ))
    #
    #
