from bs4 import BeautifulSoup as BS
import urllib as ul
import requests
import re
import numpy as np
import pandas as pd
%matplotlib inline
from matplotlib import pyplot as plt
import re
import math


class Naukri():
    
    __set_col = 0
        
    def __init__(self,url):
        self.url = url
    
    @classmethod
    def __getCol(self):
        return self.__set_col
    
    @classmethod
    def __setCol(self):
        self.__set_col = 1
    
    #Opening Url
    def openUrl(self):
        assert self.url != '', 'URL NOT PASSED'
        try:
            __urlBs = BS(requests.get(self.url).text,'lxml')
            return str(__urlBs)
        except ul.error.HTTPError as httpe:
            print(httpe)
        
    def noOfPages(self):
        b = BS(self.openUrl(),'lxml')
        totalJobs = int(re.search('\s[0-9]+',(b.find('span',class_='cnt').text.strip())).group().strip())
        #print(totalJobs)
        b = BS(str(b.find_all('div',class_='srp_container fl ')),'lxml')
        return (math.ceil(totalJobs/len(b.find_all('div',class_={'row '}))),b.find_all('div',class_={'row '}))
    
    #Card Job Links
    def getCardLinks(self,totlPages):
        jdOrg = BS(str(totalPages),'lxml')
        cLinks = jdOrg.find_all('a',class_='content')
        jdLinks = [value['href'] for value in cLinks]
        return jdLinks
    
    #Job Description
    def getJobDescription(self,jdLinks):
        
        column = ['CompanyName','Experience','Salary','Location','Industry','Area','Category','Role','RoleType','KeySkills','UG','PG','DR']
                
        #into JD
        for i in np.arange(0,len(jdLinks)):
            
            jdSoup = BS(requests.get(jdLinks[i]).text,'lxml')
            jDetails = BS(str(jdSoup.find('div',class_='hdSec')),'lxml')
            try:
                cName = jDetails.a.text.strip()
                exp = jDetails.span.text.strip()
                loc = jDetails.find('div',class_='loc collapsed').text.strip()
            except Exception as e:
                continue
				
            #Requirements
            req = []

            desc = [value.text for value in jdSoup.find('div',class_='JD').find('div',class_='jDisc mt20').find_all('p')]
            salary = desc[0].split(':')[1].strip() if desc[0].split(':')[1].strip() not in (' ',None,'') else ''
            industry = desc[1].split(':')[1].strip() if desc[1].split(':')[1].strip() not in (' ',None,'') else ''
            area =  desc[2].split(':')[1].strip() if desc[2].split(':')[1].strip() not in (' ',None,'') else ''
            category =  desc[3].split(':')[1].strip() if desc[3].split(':')[1].strip() not in (' ',None,'') else ''
            role =  desc[4].split(':')[1].strip() if desc[4].split(':')[1].strip() not in (' ',None,'') else ''
            role_type =  desc[5].split(':')[1].strip() if desc[5].split(':')[1].strip() not in (' ',None,'') else ''

            req.extend((salary,industry,area,category,role,role_type))


            #Keyskills
            keySkills = [value.text.strip()+',' for value in jdSoup.find('div',class_='ksTags').find_all('a') if value.text not in (' ',None,'')]
            keySkills = ''.join(str(value) for value in keySkills)
            
            #Education
            edu = []
            ug = ''
            pg = ''
            dr = ''
            try:
                education = [value.text.split('-')[0].split(':')[1].strip() for value in jdSoup.find('div',class_='jDisc mt10 edu').find_all('p') if value.text not in (' ',None,'')]
                ug = education[0] if education[0] not in (' ',None,'') else ''
                pg = education[1] if education[1] not in (' ',None,'') else ''
                dr = education[2] if education[2] not in (' ',None,'') else ''
            except Exception as e:
                pass

            edu.extend((ug,pg,dr))
            
            if(self.__getCol() == 0):
                data = pd.DataFrame([],columns=column)
                data.to_csv('naukri.csv',mode='w',index=False)
                self.__setCol()
            else:
                #Uneven list size
                cName = pd.Series(cName)
                exp = pd.Series(exp)
                #req = pd.Series(req,name='Requirement')
                salary = pd.Series(salary)
                loc = pd.Series(loc)
                industry = pd.Series(industry)
                area = pd.Series(area)
                category = pd.Series(category)
                role = pd.Series(role)
                role_type = pd.Series(role_type)
                keySkills = pd.Series(keySkills)
                ug = pd.Series(ug)
                pg = pd.Series(pg)
                dr = pd.Series(dr)
                data = pd.concat([cName,exp,salary,loc,industry,area,category,role,role_type,keySkills,ug,pg,dr],axis=1)
                data.to_csv('naukri.csv',mode='a',index=False,header=False)
        
    
    #Page next page you can use it if you want
    def checkNextPage(self,urlData):
        __nextLink  = BS(urlData,'lxml')
        pageNav = __nextLink.find('div',class_='pagination')
        return 1 if pageNav != None else 0
    
    #Checking next link is there or not
    def nextPageLink(self,urlData):
        __nextLink  = BS(urlData,'lxml')
        pageNav = __nextLink.find('div',class_='pagination')
        for link in pageNav:
            if(link.string == 'Next'):
                return(link['althref'])
				
if __name__ == '__main__":				
	url = "https://www.naukri.com/machine-learning-jobs"
	page = Naukri(url)
	openUrl = page.openUrl()
	totalPages = page.noOfPages()
	links = page.getCardLinks(totalPages[1])
	page.getJobDescription(links)
	for i in np.arange(2,int(totalPages[0])+1):
		page.url = url + '-'+str(i)
		urlx = page.openUrl()
		cards = page.noOfPages()[1]
		links = page.getCardLinks(cards)
		page.getJobDescription(links)
	
	#Visualization
	plt.style.available
	plt.style.use('seaborn')
	naukri = pd.read_csv('./naukri.csv',header=0)
	
	#Displaying Bar Plot
	def showBarPlot(dataframe,colname='',xlabel='X',ylabel='Y',title='Title',saveName='temp'):
		assert colname !='','NO COLUMN NAME SUPPLIED'
		naukriDf = dataframe.copy()
		df = pd.DataFrame(naukriDf.groupby(colname)[colname].count())
		df.rename(index = str, columns={colname : 'Count'},inplace=True)
		df[colname] = df.index
		df.set_axis(np.arange(1,len(df['Count'])+1),inplace=True)
		df.sort_values('Count',inplace=True)
		figure = plt.figure(figsize=(8,15))
		p = figure.add_subplot(111)
		#p.plot(df.CompanyName)
		p.barh(df[colname],df.Count,align='center',color='rgbcmyk',height=0.5)
		p.set_facecolor('w')
		plt.xticks(df.Count)
		plt.setp(p.get_xticklabels(), rotation=55, horizontalalignment='right')
		p.set(xlim=[0,max(df.Count)+min(df.Count)], xlabel=xlabel, ylabel=ylabel,title=title)

		plt.savefig(saveName+'.jpeg')
		plt.show()
		
	#Jobs by companies
	showBarPlot(dataframe=naukri,colname='CompanyName',title='Jobs In Various Companies',xlabel='Number of Jobs',ylabel='Companies',saveName='companies')
	#Jobs by location
	showBarPlot(dataframe=naukri,colname='Location',title='Jobs In Various Locations',xlabel='Number of Jobs',ylabel='Location',saveName='location')
