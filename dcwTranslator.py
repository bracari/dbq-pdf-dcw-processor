from orderedElement import Question, LabelType, OrderedElement, FieldType


def simpleCheckBoxBinder(fields, labels):
    #Checkboxes have labels to the left and are horizontally aligned with exception of bounding jitter
    y_jitter = 3.5
    bound_fields = {}

    proximity_heat_map = {}
    for field in fields:
        proximity_heat_map.update({field: []})
        for label in labels:

            x_proximity = abs(label.x - (field.x + field.w))
            y_proximity = abs(field.y - label.y)

            if y_proximity > y_jitter:
                y_proximity = 999999

#            print("{} x:{},y:{}".format(label.description, x_proximity, y_proximity))
            proximity_heat_map[field].append(x_proximity + y_proximity)

        idx = proximity_heat_map[field].index(min(proximity_heat_map[field]))
        bound_fields.update({field: labels[idx]})

    return bound_fields


def simpleTextBinder(fields, labels):

    #Text fields are to the right and are horizontally aligned with exception of bounding jitter
    y_jitter = 3.5
    bound_fields = {}

    proximity_heat_map = {}
    for field in fields:
        proximity_heat_map.update({field: []})
#        print(field.name)
        for label in labels:
            x_proximity = abs(field.x - (label.x + label.w))
            y_proximity = abs(field.y - label.y)

            if y_proximity > y_jitter:
                y_proximity = 999999

#            print("\t\t{} x:{},y:{}".format(label.description, x_proximity, y_proximity))
            proximity_heat_map[field].append(x_proximity + y_proximity)

        idx = proximity_heat_map[field].index(min(proximity_heat_map[field]))
        bound_fields.update({field: labels[idx]})

    return bound_fields


class SimpleTranslator:

    def __init__(self, question: Question):
        self.question = question
        self.labels = {}
        self.fields = {}
        self.raw_fields = []

        for type in LabelType:
            self.labels.update({type.name: []})

        for type in FieldType:
            self.fields.update({type.name: []})

        self.process_labels()
        self.process_fields()

    def add_label(self, type: LabelType, element: OrderedElement):
        element.label_type = type
        self.labels[type.name].append(element)

    def process_labels(self):
        if self.question is None or len(self.question.elements) == 0:
            return
        for draw in self.question.get_elements():
            if draw.element.tag[-4:] == 'draw' and draw.description is not None:
                description = draw.description.upper()
                if "IF " in description:
                    self.add_label(LabelType.CONDITION_LABEL, draw)
                elif ("?" in description or "DESCRIBE" in description or "INDICATE" in description) and "OTHER" not in description:
                    self.add_label(LabelType.QUESTION_LABEL, draw)
                else:
                    self.add_label(LabelType.DTA_LABEL, draw)

    def get_ordered_labels(self, type: LabelType): #Look into kwargs to allow multiple types
        return self.labels[type.name]

    def add_field(self, type: FieldType, element: OrderedElement):
        element.field_type = type
        element.label_type = LabelType.FIELD
        self.raw_fields.append(element)
        self.fields[type.name].append(element)

    def process_fields(self):
        if self.question is None or len(self.question.elements) == 0:
            return
        for field in self.question.get_elements():
            if field.element.tag[-5:] == 'field':
                checkbox = field.element.find("t:ui/t:checkButton", OrderedElement.ns)
                date = field.element.find("t:ui/t:dateTimeEdit", OrderedElement.ns)
                textbox = field.element.find("t:ui/t:textEdit", OrderedElement.ns)
                if checkbox is not None:
                    self.add_field(FieldType.ALPHA, field)
                if date is not None:
                    self.add_field(FieldType.DATE, field)
                if textbox is not None:
                    if field.h > 5:
                        self.add_field(FieldType.RICH_TEXT, field)
                    else:
                        self.add_field(FieldType.FREE_TEXT, field)

    def get_ordered_fields(self, type: FieldType): #Look into kwargs to allow multiple types
        return  self.fields[type.name]

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


