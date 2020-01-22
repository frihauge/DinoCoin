from fpdf import Template, FPDF
import os
import logging
#fpdf = FPDF()
logger = logging.getLogger(__name__)

class ReceiptRenderer():
    """docstring for ReceiptRenderer"""
    def __init__(self, size=(60, 70), root=None, widthBuffer=0, offsetLeft=0, labeltype=0):
        self.root = root
        self.path = os.path.dirname(os.path.abspath(__file__))
        if labeltype == 1:
            size=(60, 110)
        self.size = size
        self.widthBuffer = widthBuffer
        self.offsetLeft = offsetLeft
        self.labeltype = labeltype
        

        if self.labeltype == 0:
            self.dansih_label()
        if self.labeltype == 1:
            self.englishgarab_label()
               
       

    def render(self, filename, labeinfo, barcode, control_code, datecatchup):
        if isinstance(labeinfo,dict):
            prize_en =  labeinfo["LabelInfo"]['en']
            prize_arab =  labeinfo["LabelInfo"]['arab']
            pickup_en =  labeinfo["delivery_point"]['en']
            pickup_arab  =  labeinfo["delivery_point"]['arab']
        else:
            prize_en = labeinfo
            prize_arab=labeinfo
            pickup_en = datecatchup
            pickup_arab= datecatchup
            
        if self.labeltype == 0:
            return self.render_dk(filename, prize_en, barcode, control_code,pickup_en, datecatchup)
        elif self.labeltype == 1:
            return self.render_englisharab(filename, prize_en, prize_arab, barcode, control_code, pickup_en,  pickup_arab, datecatchup)
        else:
            return "Wrong label type"

    def render_dk(self, location, prize_en, barcode, control_code, pickup_en, datecatchup):
        try:
            self.document["prize"] = prize_en
            self.document["info"] = "Hent din præmie i " + pickup_en + " inden"
            self.document["date"] = datecatchup
            self.document["barcode"] = barcode
            self.document["control_code"] = "Kontrolkode:\n" + control_code
            self.document.render(location)
        except Exception as e:
            logger.error("Error Rendering ticket render_dk" +str(e))
            print(e)  
            return e
        
    def render_englisharab(self, filename, prize_en, prize_arab, barcode_en, control_code_en, pickup_en,  pickup_arab, datecatchup):
        try:
            self.document["prize_en"] = prize_en
            self.document["prize_arab"] = prize_arab
            
            self.document["pickup_en"] = "Get you prize in " + pickup_en + " before"
            self.document["pickup_arab"] = """الفائزم """ + pickup_arab + " قبل"
            self.document["date_en"] = datecatchup
            self.document["date_arab"] = datecatchup
            self.document["barcode_en"] = barcode_en
            self.document["control_code_en"] = "Verification code:\n" + control_code_en
            self.document.render(filename)
        except Exception as e:
            logger.error("Error Rendering render_englisharab ticket" +str(e))
            print(e)  
            return e
        
    def dansih_label(self):
        logger.info("Rendering ticket dansih_label")   
        offsetLeft = self.offsetLeft
        top_offset = 8
        offset_subtitle = 10
        
        offset_prizetext = 25
        offset_delivery = 37
        offset_date = 45
        offset_barcode = 60
        offset_controlcode=60
        offset_warn = 73
                
        width = self.size[0]
        removeTwoLinesOffset = 25
        height = max(width + self.widthBuffer + 5, self.size[1])
        # margin is 2% of width
        margin = width * 0.02
        endLeft = width - margin
        top = margin+top_offset
        self.elements = [
            { 
                'name': 'title', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top, 
                'x2': offsetLeft + endLeft, 
                'y2': top, 
                'font': "FlamencoD", 
                'size': 40.0, 
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
                'y1': top+offset_subtitle, 
                'x2': offsetLeft + endLeft, 
                'y2': top+offset_subtitle, 
                'font': "FlamencoD", 
                'size': 22.0, 
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
                'name': 'prize', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top+offset_prizetext, 
                'x2': offsetLeft + width - margin, 
                'y2': top+offset_prizetext, 
                'font': "Hobo", 
                'size': 22.0, 
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
                'y1':  top+offset_barcode,  
                'x2': offsetLeft + width / 2 - margin, 
                'y2':  top+offset_barcode+10,  
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
                'y1': top+offset_controlcode,   
                'x2': offsetLeft + endLeft, 
                'y2':top+offset_controlcode+5,  
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
                        { 
                'name': 'info', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top+offset_delivery, 
                'x2': offsetLeft + endLeft, 
                'y2': top+offset_delivery,  
                'font': "DINEngschrift LT", 
                'size': 15.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Hent din prÃ¦mie i informationen inden ', 
                'priority': 2, 
            },
            { 
                'name': 'date', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top+offset_date, 
                'x2': offsetLeft + endLeft, 
                'y2': top+offset_date, 
                'font': "DINEngschrift LT", 
                'size': 15.0, 
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
                'name': 'Warning', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top+offset_warn, 
                'x2': offsetLeft + endLeft, 
                'y2': top+offset_warn, 
                'font': "DINEngschrift LT", 
                'size': 7.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Gevinsten kan ikke ombyttes til andre gevinster', 
                'priority': 2, 
            },
            #{ 'name': 'box', 'type': 'B', 'x1': offsetLeft + margin, 'y1': margin, 'x2': offsetLeft + width - margin, 'y2': height - margin, 'font': 'Arial', 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 0, },
        ]
        self.document = Template(format=(width + self.widthBuffer, height), elements = self.elements, orientation="P")
        self.document.pdf.add_font('FlamencoD', '', 'flamenn_0.ttf', uni=True)
        self.document.pdf.add_font( 'DINEngschrift LT', 'I', 'lte50845.ttf', uni=True)
        self.document.pdf.add_font('Hobo', 'B', 'hobo.ttf', uni=True)
        
        self.document.add_page()
        
    def englishgarab_label(self):
   
        offsetLeft = self.offsetLeft
        top_offset = 6
        offset_subtitle_en = 15
        
        offset_prizetext_en = 26
        offset_delivery_en = 38
        offset_date_en = 44
        offset_barcode_en = 50
        offset_controlcode_en=50

           
        offset_title_arab = 67
        offset_subtitle_arab = 77
        offset_prizetext_arab = 88
        offset_delivery_arab = 98
        offset_date_arab = 105
        
        
        width = self.size[0]
        removeTwoLinesOffset = 25
        height = max(width + self.widthBuffer + 5, self.size[1])
        # margin is 2% of width
        margin = width * 0.02
        endLeft = width - margin
        top = margin
         
        self.elements = [
            { 
                'name': 'title_en', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top+top_offset, 
                'x2': offsetLeft + endLeft, 
                'y2':top+5, 
                'font': "FlamencoD", 
                'size': 40.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Winner!', 
                'priority': 2, 
            },
            { 
                'name': 'subtitle_en', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_subtitle_en, 
                'x2': offsetLeft + endLeft, 
                'y2': top +offset_subtitle_en, 
                'font': "FlamencoD", 
                'size': 22.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'you have won', 
                'priority': 2, 
            },
            { 
                'name': 'prize_en', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1':  top +offset_prizetext_en, 
                'x2': offsetLeft + width - margin, 
                'y2':  top +offset_prizetext_en, 
                'font': "Hobo", 
                'size': 22.0, 
                'bold': 1, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Teddy Bear', 
                'priority': 2, 
                'multiline': True,
            },
            { 
                'name': 'pickup_en', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1':  top +offset_delivery_en,
                'x2': offsetLeft + endLeft, 
                'y2':  top +offset_delivery_en, 
                'font': "DINEngschrift LT", 
                'size': 15.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Get your prize in Smoke-in before', 
                'priority': 2, 
            },
            { 
                'name': 'date_en', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1':  top +offset_date_en, 
                'x2': offsetLeft + endLeft, 
                'y2':  top +offset_date_en,  
                'font': "DINEngschrift LT", 
                'size': 15.0, 
                'bold': 0, 
                'italic': 1, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'Todays date', 
                'priority': 2, 
            },

            { 
                'name': 'barcode_en', 
                'type': 'BC', 
                'x1': offsetLeft + margin + width * 0.05, 
                'y1': top +offset_barcode_en, 
                'x2': offsetLeft + width / 2 - margin, 
                'y2': top +offset_barcode_en+10, 
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
                'name': 'control_code_en', 
                'type': 'T', 
                'x1': offsetLeft + width / 2 + margin, 
                'y1': top +offset_controlcode_en, 
                'x2': offsetLeft + endLeft+2, 
                'y2': top +offset_controlcode_en+4, 
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
              { 
                'name': 'title_arab', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_title_arab, 
                'x2': offsetLeft + endLeft, 
                'y2': top +offset_title_arab, 
                'font': "DejaVu", 
                'size': 32.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': u"""لقد فزت """,
                'priority': 2, 
            },
            { 

                'name': 'subtitle_arab', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_subtitle_arab, 
                'x2': offsetLeft + endLeft, 
                'y2': top +offset_subtitle_arab, 
                'font': "DejaVu", 
                'size': 15.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': u"""لقد فزت""", 
                'priority': 2, 
            },
            { 
                'name': 'prize_arab', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_prizetext_arab, 
                'x2': offsetLeft + width - margin, 
                'y2': top +offset_prizetext_arab, 
                'font': "DejaVu", 
                'size': 16.0, 
                'bold': 0, 
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
                'name': 'pickup_arab', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_delivery_arab, 
                'x2': offsetLeft + endLeft, 
                'y2': top +offset_delivery_arab, 
                'font': "DejaVu", 
                'size': 10.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'الحصول على الجائزة الخاصة بك من قب,',
                'priority': 2, 
            },
            { 
                'name': 'date_arab', 
                'type': 'T', 
                'x1': offsetLeft + margin, 
                'y1': top +offset_date_arab, 
                'x2': offsetLeft + endLeft, 
                'y2': top +offset_date_arab, 
                'font': "DejaVu", 
                'size': 10.0, 
                'bold': 0, 
                'italic': 0, 
                'underline': 0, 
                'foreground': 0, 
                'background': 0, 
                'align': 'C', 
                'text': 'ريخ اليوم', 
                'priority': 2, 
            },

            #{ 'name': 'box', 'type': 'B', 'x1': offsetLeft + margin, 'y1': margin, 'x2': offsetLeft + width - margin, 'y2': height - margin, 'font': 'Arial', 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 0, },
        ]
        self.document = Template(format=(width + self.widthBuffer, height), elements = self.elements, orientation="P")
        self.document.pdf.add_font('FlamencoD', '', 'flamenn_0.ttf', uni=True)
        self.document.pdf.add_font( 'DINEngschrift LT', 'I', 'lte50845.ttf', uni=True)
        self.document.pdf.add_font('Hobo', 'B', 'hobo.ttf', uni=True)
        self.document.pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
       
        
        self.document.add_page()       
        
if __name__ == '__main__':
    labeinfo = dict()
    labeinfo["LabelInfo"] = dict()
    labeinfo["delivery_point"] = dict()
    labeinfo["LabelInfo"]['da'] = 'Superfantastiske'
    labeinfo["LabelInfo"]['en'] ='Teddy Bear'
    labeinfo["LabelInfo"]['arab'] ='Teddy Bear'
    labeinfo["delivery_point"]['da'] ='Smoke-In'
    labeinfo["delivery_point"]['en'] ='Smoke-In'
    labeinfo["delivery_point"]['arab'] = 'Smoke-In'
    r = ReceiptRenderer(widthBuffer=20, offsetLeft=8,labeltype=0)
   # r.render("receipt_test.pdf", labeinfo, "1231231231", "V3RY53CR37",'d.12/12-2019')
   # r.render_englisharab(filename="receipt_test.pdf", prize_en="Teddy Bear", prize_arab="Teddy Bear", barcode_en="1231231231", control_code_en="V3RY53CR37",pickup_en="Smoke-In",pickup_arab='Smoke-In' ,datecatchup='d.12/12-2019')
    r.render("receipt_test.pdf", labeinfo, "1231231231", "V3RY53CR37",'d.12/12-2019')
   