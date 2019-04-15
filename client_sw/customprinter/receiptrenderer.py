from fpdf import Template, FPDF

#fpdf = FPDF()


class ReceiptRenderer():
    """docstring for ReceiptRenderer"""
    def __init__(self, size=(60, 70), widthBuffer=0, offsetLeft=0):
        width = size[0]
        removeTwoLinesOffset = 25
        height = max(width + widthBuffer + 5, size[1])
        # margin is 2% of width
        margin = width * 0.02
        endLeft = width - margin

        self.elements = [
            { 
                'name': 'title', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': margin, 
                'x2': offsetLeft + endLeft, 
                'y2': height * 0.2, 
                'font': "FlamencoD", 
                'size': 32.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Tillykke', 
                'priority': 2, 
            },
            { 
                'name': 'subtitle', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': height * 0.2, 
                'x2': offsetLeft + endLeft, 
                'y2': height * 0.3, 
                'font': "FlamencoD", 
                'size': 15.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Du har vundet:', 
                'priority': 2, 
            },
            { 
                'name': 'info', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': height * 0.75 - removeTwoLinesOffset, 
                'x2': offsetLeft + endLeft, 
                'y2': height * 0.85 - removeTwoLinesOffset, 
                'font': "DINEngschrift LT", 
                'size': 10.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Hent din præmie i informationen inden ', 
                'priority': 2, 
            },
            { 
                'name': 'date', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': height * 0.75 - removeTwoLinesOffset, 
                'x2': offsetLeft + endLeft, 
                'y2': height * 0.85 - removeTwoLinesOffset, 
                'font': "DINEngschrift LT", 
                'size': 10.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Dags dato', 
                'priority': 2, 
            },
            { 
                'name': 'prize', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': height * 0.35, 
                'x2': offsetLeft + width - margin, 
                'y2': height * 0.42, 
                'font': "hobo", 
                'size': 16.0, 
                'bold': 1, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': '', 
                'priority': 2, 
                'multiline': True,
            },
            { 
                'name': 'barcode', 
                'type': 'BC', 
                'x1': offsetLeft + margin + width * 0.05, 
                'y1': height - margin - height * 0.1 - removeTwoLinesOffset, 
                'x2': offsetLeft + width / 2 - margin, 
                'y2': height - margin - 2 - removeTwoLinesOffset, 
                'font': 'Interleaved 2of5 NT', 
                'size': 1, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'I', 
                'text': '8120081878', 
                'priority': 3, 
            },
            { 
                'name': 'control_code', 
                'type': 'T', 
                'x1': offsetLeft + width / 2 + margin, 
                'y1': height - 11 - margin - removeTwoLinesOffset, 
                'x2': offsetLeft + endLeft, 
                'y2': height - 6 - margin - removeTwoLinesOffset, 
                'font': 'Arial', 
                'size': 8.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0x000000, 
                'background': 0x000000, 
                'align': 'R', 
                'text': 'Kontrolkode:\nAkdj32', 
                'priority': 3, 
                'multiline': True,
            },
            #{ 'name': 'box', 'type': 'B', 'x1': offsetLeft + margin, 'y1': margin, 'x2': offsetLeft + width - margin, 'y2': height - margin, 'font': 'Arial', 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 0, },
        ]
        self.document = Template(format=(width + widthBuffer, height), elements = self.elements, orientation="P")
        
        self.document.pdf.add_font('Hobo', 'B', 'hobo.ttf', uni=True)
        self.document.pdf.add_font('FlamencoD', '', 'flamenn_0.ttf', uni=True)
        self.document.pdf.add_font('DINEngschrift LT', 'I', 'lte50845.ttf', uni=True)
        
        self.document.add_page()

    def render(self, location, prize, barcode, control_code, info_text):
        self.document["prize"] = prize
        self.document["info"] = info_text 
        self.document["date"] = "19 / 4 -2019" 
        self.document["barcode"] = barcode
        self.document["control_code"] = "Kontrolkode:\n" + control_code
        self.document.render(location)
    


if __name__ == '__main__':
    r = ReceiptRenderer(widthBuffer=20, offsetLeft=8)
    r.render("receipt_test.pdf", "Superfantastiske", "1231231231", "V3RY53CR37","afhentet i information inden  \n\r dagas dato ")
