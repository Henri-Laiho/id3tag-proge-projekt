import re

# nimekiri veergudest, mille korral saab ette arvata failinime põhjal
filename_usable = {9:'Title', 10:'Artist', 11:'Album', 12:'Album Artist',
                   14:'tracknumber', 15:'Year', 16:'Conductors',
                   17:'Composer', 18:'Writer'}

class NameFormat:
    
    def __init__(self, columns):
        # viide veergudele
        self.cols = columns
        self.space_before_capital = True
        
        # eraldajad failinimes, alguses eeldame kõik mitte tähestikulised tähemärgid
        self.separators = '\\'+'\\'.join([chr(x) for x in range(32, 127) if not chr(x).isalnum()])
        
    #def learn(self, column, filename, userinput):
        #userin = userinput.lower()
        #name = filename.lower()
        
        #i = name.find(userin)
        #if i > -1:
            
        
    # returnib listi võimalikest valikutest mälu ja/või failinime põhjal
    # memory on list asjadest, mida kasutaja on sellesse veergu sisestanud
    def guess(self, filename, column, memory = []):
        # kui antud veerg on ette arvatav failinime põhjal
        if column in filename_usable:
            options = list(filter(None, re.split('['+self.separators+']+', filename)))
            
            # juhuks kui nimes on sõnad kokku kirjutatud aga iga sõna algab suure tähega
            # paneb tühiku iga suurtähe ette
            if self.space_before_capital:
                for i in range(len(options)):
                    for k in range(1, len(options[i])-1):
                        if options[i][k].isupper() and options[i][k+1].islower() and options[i][k-1] != ' ':
                           options[i] = options[i][:k] + ' ' + options[i][k:]
                           k += 1
            
            return options
        else:
            return []
    
    
    
    
    
    