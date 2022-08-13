#%%

# this parser has been coded thanks to https://gist.github.com/nathan-sixnines/69bb7379c33d00917c3f2f5c0cef0612 

# ENCOD = 'iso-8859-9'
from ast import parse
import re
from pprint import pprint

ENCOD = 'utf-8'
def pdf_to_csv(filename, separator, threshold):
    from io import StringIO
    from pdfminer.converter import LTChar, TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage

    class CsvConverter(TextConverter):
        def __init__(self, *args, **kwargs):
            TextConverter.__init__(self, *args, **kwargs)
            self.separator = separator
            self.threshold = threshold

        def end_page(self, i):
            from collections import defaultdict
            lines = defaultdict(lambda: {})
            for child in self.cur_item._objs:
                if isinstance(child, LTChar):
                    (_, _, x, y) = child.bbox
                    line = lines[int(-y)]
                    line[x] = child._text.encode(ENCOD)
            for y in sorted(lines.keys()):
                line = lines[y]
                self.line_creator(line)
                self.outfp.write(self.line_creator(line))
                self.outfp.write("\n")

        def line_creator(self, line):
            keys = sorted(line.keys())
            average_distance = sum([keys[i] - keys[i - 1] for i in range(1, len(keys))]) / len(keys)
            result = [line[keys[0]].decode(ENCOD)]
            for i in range(1, len(keys)):
                if (keys[i] - keys[i - 1]) > average_distance * self.threshold:
                    result.append(self.separator)
                result.append(line[keys[i]].decode(ENCOD))
            printable_line = ''.join(result)
            return printable_line

    rsrc = PDFResourceManager()
    outfp = StringIO()
    device = CsvConverter(rsrc, outfp, laparams=LAParams())

    fp = open(filename, 'rb')

    interpreter = PDFPageInterpreter(rsrc, device)
    for i, page in enumerate(PDFPage.get_pages(fp)):
        outfp.write("START PAGE %d\n" % i)
        if page is not None:
            # print('none')
            interpreter.process_page(page)
        outfp.write("END PAGE %d\n" % i)

    device.close()
    fp.close()

    return outfp.getvalue()


if __name__ == '__main__':
    separator = ';'
    threshold = 1.3 #1.5
    cikti = pdf_to_csv('ts.pdf', separator, threshold)

    cikti = cikti.replace("\xa0", " ")

    # f = open("parsed-pdf.csv", "w")
    # f.write(cikti)
    # f.close()


    regx_class = r"([A-Za-zÇÖİŞÜĞçöışüğ]+[0-9]+;[A-Za-z0-9ÇÖİŞÜĞçöışüğ\s\.\(\)\/\\\+\{\}]*;\d*[,\d]*;\d*[,\d]*;\d*[,\d]*;[A-Z]{0,2})"
    

    parsed = cikti.split("\n")
    parsed_mat = []
    donemler = []
    donem_tmp = {}
    for i in range(len(parsed)):
        p = parsed[i]
        l = p.split(";")
        l_to_add = []
        for l2 in l:
            l_to_add.append(l2.strip())
        parsed_mat.append(l_to_add)

        if p.startswith("Ders Kodu"):
            if 'donem' in donem_tmp:
                donemler.append(donem_tmp)
                donem_tmp = {}
            donem_tmp['donem'] = parsed[i-1].replace(";","")
            donem_tmp['dersler'] = []
        else:
            found_classes = re.findall(regx_class, p)
            for fcls in found_classes:
                ifc = fcls.split(";")
                donem_tmp['dersler'].append([ifc[0], ifc[1], ifc[-1]])
                # print(ifc[0], ifc[1], ifc[-1])
            
            if p.startswith("AGNO"):
                donem_tmp['agno'] = float(l[1].replace(",","."))
            if p.startswith("ANO"):
                donem_tmp['ano'] = float(l[1].replace(",","."))
    
    if 'donem' in donem_tmp:
        donemler.append(donem_tmp)
        donem_tmp = {}
        

    
    print("Adı: ",parsed_mat[4][0])
    print("Son AGNO: ",donemler[-1]['agno'])

    pprint(donemler)
    
    gerekli_dersler = [ "Bilgisayar Mühendisliğine Giriş",
                        "Algoritmalar ve Programlama",
                        "English I",
                        "Fizik I",
                        "Matematik I",
                        "Lineer Cebir",
                        "Türk Dili I",
                        
                        "Atatürk İlkeleri ve İnkılap Tarihi I",
                        "Ayrık Yapılar",
                        "Veri Yapıları",
                        "İş Sağlığı ve Güvenliği I",
                        "Diferansiyel Denklemler",
                        "Elektronik I",
                        "Mantık Devreleri",
                        # "Sosyal Seçmeli Ders",


                        "Biçimsel Diller ve Otomata Teorisi",
                        "Mikroişlemciler",
                        "Algoritma Analizi ve Tasarımı",
                        # "Teknik Seçmeli Ders",
                        # "Teknik Seçmeli Ders",
                        # "Teknik Seçmeli Ders"
                        ]
    



    #".*;.*;.*;.*;\d*(,\d)*;.*"
    #[A-Za-z0-9ÇÖİŞÜĞçöışüğ]*;[A-Za-z0-9ÇÖİŞÜĞçöışüğ]*;\d*[,\d]*;\d*[,\d]*;\d*[,\d]*;[a-z]{0,2}
    #(.*;.*;\d*[,\d]*;\d*[,\d]*;\d*[,\d]*;.*)
    # regx = r"([A-Za-zÇÖİŞÜĞçöışüğ]+[0-9]+;[A-Za-z0-9ÇÖİŞÜĞçöışüğ\s\.\(\)\/\\\+]*;\d*[,\d]*;\d*[,\d]*;\d*[,\d]*;[A-Z]{0,2})"
    # found_classes = re.findall(regx, cikti)
    # # print(found_classes)
    # # print(len(found_classes))
    # print("Alınan ders sayısı:",len(found_classes))

    # for fcls in found_classes:
    #     ifc = fcls.split(";")
    #     print(ifc[0], ifc[1], ifc[-1])
    

    
    
    
