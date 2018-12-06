import os
import pandas as pd
from difflib import SequenceMatcher
import re
import ftfy


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class session:
    
    session_count = 0
    
    def __init__(self):
        self.string_list = ["empty"]
        self.Interview = ["empty"]
        self.Ticker = "empty"
        self.Year = "empty"
        self.Quarter = "empty"
        self.CEOname = "empty"
        self.CEOtext = "empty"
        self.Analysttext = "empty"
        self.Tags = ["empty"]
        self.CEOTag = "empty"
        self.CompanyName = "empty"
        self.ExecText = "empty"
        self.Date = "empty"
        self.Execs = ["empty"]
        self.Analysts = ["empty"]
        self.OtherExecsTags = ['empty']
        self.AnalystTags = ["empty"]
        session.session_count+=1
        
    def fix_utf(self):
        temp_arr = ["empty"]
        for string in self.string_list:
            if type(string) != str:
                string = string.decode("utf-8")
            
            string = ftfy.fix_text(string)
            string = string.replace("â€“", "-")
            string = string.replace(u"\xad", " - ")
            temp_arr.append(string)
        temp_arr.pop(0)
        self.string_list = temp_arr

    def getDate(self):
        found = False
        for string in self.string_list:
            string = string.replace(u'\xa0', ' ')
            date_format = re.compile('.*\. .*, [2][0-9][0-9][0-9] .*:.*')
            if date_format.match(string) is not None:
                found = True
                try:
                    date = string.split("PM")[0]
                    self.Date = date + " PM"
                    print(self.Date)
                    break
                except:
                    try: 
                        date = string.split("AM")[0]
                        self.Date = date + "AM"
                        print(self.Date)
                        break
                    except:
                        raise Exception("Could not split date")
        if not found:
            print("Date not found")
    def getExecs(self, org_df):
        Recording = False
        for line in self.string_list:
            if not Recording:
                if line == 'Executives\n':
                    Recording = True
            else:
                if line == 'Analysts\n':
                    break
                else:
                    try:
                        exec_name = line.split(' - ')[0]
                        exec_title = line.split(' - ')[1]
                        exec_title = exec_title.replace(u"\xa0", ' ')
                        exec_name = exec_name.rstrip()
                        self.Execs.append(exec_name)
                        if "CEO" in exec_title or "Chief Executive Officer" in exec_title:
                            self.CEOname = exec_name
                    except:
                        try:
                            exec_name = line.split('–')[0]
                            exec_title = line.split('–')[1]
                            exec_title = exec_title.replace(u'\xa0', ' ')
                            exec_name = exec_name.rstrip()
                            self.Execs.append(exec_name)
                            if "CEO" in exec_title or "Chief Executive Officer" in exec_title:
                                self.CEOname = exec_name
                        except:
                            print(line.split())
                            print('fucks')
        self.Execs.pop(0)
        if self.CEOname == "empty":
            company_df = org_df[org_df['Ticker'] == self.Ticker]
            ceo_name = company_df["CEO_Name"].values[0]
            for exec_ in self.Execs:
                isceo = True
                for name in ceo_name.split():
                    if name not in exec_:
                        isceo = False
                        break
                if isceo:
                    self.CEOname = exec_
        print(self.CEOname)
        #print(self.Execs)

    def getAnalysts(self):
        Recording = False
        form = re.compile('.* - .*')
        form_2 = re.compile('.* – .*')
        for line in self.string_list:
            if not Recording:
                if line == 'Analysts\n':
                    Recording = True
            else:
                if "Operator" in line:
                    break
                else:
                    try:
                        analyst_name = line.split('-')[0]
                        analyst_company = line.split('-')[1]
                        #analyst_name = analyst_name.replace(u'\xa0', ' ')
                        analyst_name = analyst_name.rstrip()
                        self.Analysts.append(analyst_name)
                    except:
                        try:
                            analyst_name = line.split('–')[0]
                            analyst_company = line.split('–')[1]
                            #analyst_name = analyst_name.replace(u'\xa0', ' ')
                            analyst_name = analyst_name.rstrip()
                            self.Analysts.append(analyst_name)
                        except:
                            pass


        self.Analysts.pop(0)
        #print(self.Analysts)

    def IsolateInterview(self):
        if "Questions and Answers\n" in self.string_list:
            start = self.string_list.index("Questions and Answers\n")
        if "QUESTIONS AND ANSWERS\n" in self.string_list:
            start = self.string_list.index("QUESTIONS AND ANSWERS\n")
        if "Question-and-Answer Session\n" in self.string_list:
            start = self.string_list.index("Question-and-Answer Session\n")
        for string in self.string_list:
            if "Question" in string and "and" in string and "Answer" in string \
            and "Session\n" in string:
                start = self.string_list.index(string)
        self.Interview = self.string_list[start:]

    def removeFluff(self):
        i = 0
        for string in self.string_list:
            if "https:" in string or "Earnings Call Transcript | Seeking Alpha" in string:
                self.string_list.pop(i)
            i += 1

    def getTags(self):
        tag_format = re.compile('.* - .*\n')
        for line in self.Interview:
            #print(line)
            tag = False
            for exec_ in self.Execs:
                if tag_format.match(line) is not None \
                and 'Seeking Alpha' not in line and exec_ in line:
                    self.Tags.append(line)
                    tag = True
                elif (exec_ + '\n') in line:
                    if line not in self.Tags:
                        self.Tags.append(line)
                        tag = True
            if not tag:
                for analyst in self.Analysts:
                    if (tag_format.match(line) is not None \
                    and 'Seeking Alpha' not in line) and analyst in line:
                            self.Tags.append(line)
                    elif (analyst + '\n') == line:
                        if line not in self.Tags:
                            self.Tags.append(line)
        #print(self.Tags)
    def getCEOTag(self):
        name = self.CEOname
        print(name)
        for tag in self.Tags:
            if self.CEOname in tag:
                self.CEOTag = tag
                break
        if self.CEOTag == "empty":
            raise ValueError("No CEO Tag Found\n")
    def getOtherExecsTags(self):
        for tag in self.Tags:
            for exec_ in self.Execs:
                if exec_ != self.CEOname:
                    if exec_ in tag:
                        self.OtherExecsTags.append(tag)
        self.OtherExecsTags.pop(0)

    def getAnalystTags(self):
        for tag in self.Tags:
            for analyst in self.Analysts:
                if analyst in tag:
                    self.AnalystTags.append(tag)
        self.AnalystTags.pop(0)

    def grabCEOtext(self):
        """Grabs the CEO's title and creates a list with all the text spoken by the CEO"""
        CEOtext=[]
        Recording=False
        for string in self.Interview:
            if Recording:
                if string in self.Tags and string != self.CEOTag:
                    Recording = False
                else:
                    CEOtext.append(string)
            else:
                if string == self.CEOTag:
                    Recording=True
                    CEOtext.append(string)
        self.CEOtext = " ".join(CEOtext)

    def grabOtherExectext(self):
        """ Gets the text of the other executives, not the CEO, on the call """
        Exectext = []
        Recording = False
        for string in self.Interview:
            if Recording:
                if string in self.Tags:
                    if string not in self.OtherExecsTags:
                        Recording = False
                else:
                    Exectext.append(string)
            else:
                if string in self.Tags and string in self.OtherExecsTags:
                    Recording = True
                    Exectext.append(string)
                    #print(string)
        self.ExecText = " ".join(Exectext)

    def grabAnalysttext(self):
        """Creates a list with all the text from anyone with the title of Analyst"""
        Analysttext=[]
        Recording=False
        for string in self.Interview:
            if Recording:
                if string in self.Tags and string not in self.AnalystTags:
                    Recording = False
                else:
                    Analysttext.append(string)
            else:
                if string in self.AnalystTags:
                    Recording=True
                    Analysttext.append(string)
        self.Analysttext = " ".join(Analysttext)

    def clean(self):
        self.CEO = self.CEOname.replace(u"\xa0", " ")

    def Candidate(self):
        if ("QUESTIONS AND ANSWERS\n" in self.string_list \
        or "Questions and Answers\n" in self.string_list \
        or "Question-and-Answer Session\n" in self.string_list) \
        and (len([x for x in self.string_list if "CEO" in x])>0 \
        or len([x for x in self.string_list if "Chief Executive Officer" in x])>0):  
            return True
        else:
            return False

    def Fill(self, org_df):
        self.fix_utf()
        self.removeFluff()
        self.getDate()
        self.getExecs(org_df)
        self.getAnalysts()
        self.IsolateInterview()
        self.getTags()
        self.getCEOTag()
        self.getOtherExecsTags()
        self.getAnalystTags()
        self.grabCEOtext()
        self.grabOtherExectext()
        self.grabAnalysttext()
        self.clean()

    def count_reset():
        session.filecount = 0




def import_text(folder_path):
    folder = []
    for filename in os.listdir(folder_path):
        print(filename)
        if 'txt' in filename:
            with open (folder_path+"/"+filename, "r", encoding='utf8') as myfile:
                file_obj = session()
                file_obj.string_list = myfile.readlines()
                file_obj.Ticker = filename[:find_nth(filename,"_",1)]
                file_obj.Year = "20"+filename[find_nth(filename,"_",1)+1:find_nth(filename,"_",2)]
                file_obj.Quarter = filename[find_nth(filename,"_",2)+1:filename.index(".")]            
                folder.append(file_obj)
    return folder

    
def CreateDataframe(folder_path, org_df):
    """Returns a dataframe with year, quarter, ceo, company ticker, the Q&A text,
    and aggregated text from the CEO and Analysts"""
    
    folder = import_text(folder_path)
    df = pd.DataFrame()
    
    #get data from wikipedia to find sectors
    wiki_data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    wiki_table = wiki_data[0]
    i=0
    for file in folder:
        print("%s %s %s" %(file.Ticker, file.Quarter, file.Year))
        file.Fill(org_df)
        Year = file.Year
        Quarter = file.Quarter
        CEOname = file.CEOname
        Ticker = file.Ticker
        Interview = " ".join(file.Interview)
        CEO_Text = file.CEOtext
        AnalystText = file.Analysttext
        ExecText = file.ExecText
        date = file.Date
        print(Ticker)
        wiki_row = wiki_table[wiki_table[0] == Ticker]
        Sector = wiki_row[3].values[0]
        newDF = pd.DataFrame({"Year":Year,"Quarter":Quarter,"CEO":CEOname,\
                   "Ticker":Ticker,"Complete_Text":Interview,"CEO_Text":CEO_Text,
                   "Analyst_Text":AnalystText, "Other_Exec_Text":ExecText, "Date":date, "Sector":Sector}, index=[i])
        print(newDF["Sector"])
        df = df.append(newDF, ignore_index = True)
        i+=1
    return df