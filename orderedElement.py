from enum import Enum, IntFlag
from operator import methodcaller
import math

class LabelType(Enum):
    FIELD = 1
    QUESTION_LABEL = 2
    CONDITION_LABEL = 3
    DTA_LABEL = 4

class FieldType(IntFlag):
    ALPHA = 1
    MULTI_ALPHA = 2
    FREE_TEXT = 4
    RICH_TEXT = 8
    NUMERIC = 16
    DATE = 32


class OrderedElement:
    ns = {'xdp': 'http://ns.adobe.com/xdp/',
          't': 'http://www.xfa.org/schema/xfa-template/2.8/',
          'xmlns': 'http://www.w3.org/1999/xhtml'}

    def order(self):
        return math.ceil(self.y / 7) * 1000 + self.x

    def __init__(self, element):
        #Set name
        name = element.attrib['name'] if 'name' in element.attrib else None
        self.name = name

        #Set x-value
        x_str = element.attrib['x'] if 'x' in element.attrib else '9999mm'
        self.x = float(x_str[:-2])

        #Set y-value
        y_str = element.attrib['y'] if 'y' in element.attrib else '0mm'
        self.y = float(y_str[:-2])
        
        #Set h-value
        h_str = element.attrib['h'] if 'h' in element.attrib else '0mm'
        self.h = float(h_str[:-2])
        
        #Set w-value
        w_str = element.attrib['w'] if 'w' in element.attrib else '0mm'
        self.w = float(w_str[:-2])

        #Process and set description (Only applies to draw-type elements)
        description = None
        text_element = element.find(".//t:value/t:text", OrderedElement.ns)
        formatted_text_element = element.find(".//t:value/t:exData", OrderedElement.ns)
        if text_element is not None:
            description = text_element.text
        if formatted_text_element is not None:
            content = []
            for para in formatted_text_element.findall(".//xmlns:body/xmlns:p", OrderedElement.ns):
                content.append(para.text.strip())
            for para in formatted_text_element.findall(".//xmlns:body/xmlns:p/xmlns:span", OrderedElement.ns):
                content.append(para.text.strip())
            description = "".join(content)
        self.description = description

        self.element = element
        self.element_type = None
        self.label_type = None
        self.field_type = None

        # tag = element.tag
        # if tag[-4:] == 'draw' and description is not None:
        #     if "IF" in description.upper():
        #         self.type = Type.CONDITION_LABEL
        #     elif "SECTION" in description.upper():
        #         self.type = Type.HEADER
        #     elif "?" in description or "DESCRIBE" in description.upper() or "INDICATE" in description.upper():
        #         self.type = Type.LABEL
        #     else:
        #         self.type = Type.DTA
        #
        # else:
        #     self.type = Type.DTA
        #     checkbox = element.find("t:ui/t:checkButton", ns)
        #     textbox = element.find("t:ui/t:textEdit", ns)
        #     if checkbox is not None:
        #         self.field_type = FieldType.ALPHA
        #     if textbox is not None:
        #         h_str = element.attrib['h'] if 'h' in element.attrib else '1mm'
        #         h = float(h_str[:-2])
        #         if h > 5:
        #             self.field_type = FieldType.RICH_TEXT
        #         else:
        #             self.field_type = FieldType.FREE_TEXT


class Section:
    def order(self):
        return self.header.y

    def __init__(self, header):
        self.upper = header.y
        self.lower = 9999

        self.header = header
        self.questions = []
        self.dta_questions = []


class Question:
    def add_element(self, ordered_element: OrderedElement):
        # relative_y = ordered_element.y - self.upper
        # #relative_y = ordered_element.y
        # org_x = ordered_element.x
        # org_name = ordered_element.name
        # org_description = ordered_element.description
        # org_element = ordered_element.element
        self.elements.append(OrderedElement(ordered_element.element  ))

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


class DTAQuestion(Question):

    def mapper(self, binder):
        for bound_field in binder:
            if self.upper > bound_field.y:
                continue
            if self.lower < bound_field.y:
                break
            field_label = binder[bound_field]
            if field_label.description not in self.dta_elements:
                self.dta_elements.update({field_label.description: []})
            self.dta_elements[field_label.description].append(bound_field.field_type)

    def __init__(self, upper_bound, lower_bound, label):
        super().__init__(upper_bound, lower_bound)
        self.dta_elements = {}
        self.label = label
        self.mnemonic = label.description

