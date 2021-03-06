import xml.etree.ElementTree as ET
import re

MARKER = '_'
UNK = MARKER+'unk'

class Generator:
    def __init__(self,root):
        self.keywords = []
        self.phrase = ""
        self.tab = ""
        self.parse(root)
        self.lines = []
        # print(self.keywords)
        # print(self.phrase)
        # print(self.tab)
        self.permute(self.phrase,self.tab,0)
        tlines = list(self.lines)
        self.lines = []
        for l in tlines:
            nlines = list(self.noisify(l))
            #for lll in nlines:
                #print(lll)
            for l in nlines:
                l = self.var_resolve(l)
                self.lines.append(l)
                pass
        self.lines = sorted(list(set(self.lines)))
    def parse(self,o):
        for o2 in o:
            if o2.tag == "phrase":
                o2t = re.sub('\s+',' ',o2.text.strip())
                self.phrase = o2t
            elif o2.tag == "tab":
                self.tab = ET.tostring(o2[0], encoding='unicode')
                self.tab = re.sub("\s\s+" ,""   ,self.tab)
                self.tab = re.sub("\n"  ,""   ,self.tab)
                self.tab = re.sub(">"   ,"> " ,self.tab)
                self.tab = re.sub("<"   ," <" ,self.tab)
                self.tab = re.sub("="   ," = " ,self.tab)
                self.tab = re.sub('\"'   ," \" " ,self.tab)
            elif o2.tag == "key":
                kdict = {}
                idx = 0
                for o3 in o2:
                    idx+=1
                    phrases = []
                    for p in o3.text.split('\n'):
                        pp = re.sub('\s+'," ",p.strip()).strip()
                        if pp:
                            phrases.append(re.sub('\s+'," ",pp))
                    if o3.get("name"):
                        kdict[o3.get("name")] = phrases
                    else:
                        kdict[str(idx)] = phrases
                self.keywords.append(kdict)
    def permute(self,line,tab,keyidx):
        if keyidx >= len(self.keywords):
            #print(line,"\t\t",tab)
            self.lines.append(line+"\t"+tab)
            return
        #print("lol")
        for op in self.keywords[keyidx]:
            if op:
                mytab = re.sub(MARKER+"key"+str(keyidx+1),op,tab)
            else:
                mytab = tab
            for k in self.keywords[keyidx][op]:
                myline = re.sub(MARKER+"key"+str(keyidx+1),k,line)
                for i,key in enumerate(self.keywords):
                    if i!=keyidx:
                        self.permute(myline,mytab,keyidx+1)
                if(len(self.keywords)==1):
                    self.lines.append(myline+"\t"+mytab)
    def noisify(self,line):
        noise_level = 3
        left = line.split('\t')[0]
        tab = line.split('\t')[1]
        lines = []
        for n1 in range(0,noise_level+1):
            for n2 in range(0,noise_level+1):
                for n3 in range(0,noise_level+1):
                    for n4 in range(0,noise_level+1):
                        for n5 in range(0,noise_level+1):
                            n = 0
                            line = ""
                            for w in left.split():
                                if MARKER+"noise" in w:
                                    n+=1
                                    if w[-2].isnumeric():
                                        nmax=int(w[-1]) 
                                    else:
                                        nmax = 5
                                    if n1!=0 and n == 1:
                                        for _ in range(0,min(n1,nmax)):
                                            line += UNK+" "
                                    if n2!=0 and n == 2:
                                        for _ in range(0,min(n2,nmax)):
                                            line += UNK+" "
                                    if n3!=0 and n == 3:
                                        for _ in range(0,min(n3,nmax)):
                                            line += UNK+" "
                                    if n4!=0 and n == 4:
                                        for _ in range(0,min(n4,nmax)):
                                            line += UNK+" "
                                    if n5!=0 and n == 5:
                                        for _ in range(0,min(n5,nmax)):
                                            line += UNK+" "
                                else:
                                    line += w+" "
                            lines.append(line+"\t"+tab)
        return sorted(list(set(lines)))
    def var_resolve(self,line):
        left = line.split('\t')[0]
        tab = line.split('\t')[1]
        line = ""
        v = 0
        var_ids={}
        for i,w in enumerate(left.split()):
            if w[0] == MARKER and MARKER+"var" in w:
                v+=1
                var_ids[v] = i+1
                line += UNK+" "
            else:
                line += w+" "
        line+='\t'
        v = 0
        for i,w in enumerate(tab.split()):
            if w[0] == MARKER and MARKER+"var" in w:
                if not w[-1].isnumeric():
                    v+=1
                    line += MARKER+str(var_ids[v])+" "
                else:
                    line += MARKER+str(var_ids[int(w[-1])])+" "
            else:
                line += w+" "
        return line
def parse_xml(path=""):
    import os
    lines = []
    langdict = {}

    for filename in os.listdir("generators"):
        if filename.endswith(".xml"): 
            print("parsing...",filename)
            path = os.path.join("generators", filename)
            root = ET.parse(path).getroot()
            for o in root:
                if o.tag == "generator":
                    g = Generator(o)
                    lines += g.lines
                if o.tag == "language":
                    langs = o.get("name").split(",")
                    for l in langs:
                        if not o.get("name") in langdict:
                            langdict[o.get("name")] = {}
                        for oo in o:
                            if oo.tag == "tag":
                                ostr = re.sub("\n","",oo.text.strip())
                                ostr = re.sub("\s\s+"," ",ostr.strip())
                                langdict[o.get("name")][oo.get("name")] = ostr.strip()
            #print(langdict['python'].keys())
    return lines,langdict