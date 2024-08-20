import os
from selenium import webdriver
import time


#url = "https://canmore.org.uk/collection/1296893"
url = "https://maps.nls.uk/view/74965586"
#//*[@id=\"zoomify-container\"]/div[3]/div[2]/div[2]/button
#//*[@id="zoomify-container"]/div[3]/div[2]/div[2]/button
#/html/body/div[3]/div/div/section/div[2]/div/section/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[3]/div[2]/div[2]/button

driver = webdriver.PhantomJS("./phantomjs", service_args=[
	'--ignore-ssl-errors=true', 
	'--ssl-protocol=any', 
	#'--debug=true', 
	#'--web-security=no',
	#'--ssl-client-certificate-file=C:\tmp\clientcert.cer', 
	#'--ssl-client-key-file=C:\tmp\clientcert.key', 
	#'--ssl-client-key-passphrase=1111' 
])
#driver.set_window_size(5120, 2880)
driver.set_window_size(2560, 1440)
driver.get(url)
time.sleep(10)

# PROBLEM: the zoomify element isn't loading properly... An SSL problem? Headers problem? 

#driver.find_element_by_xpath("/html/body/div[3]/div/div/section/div[2]/div/section/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[3]/div[2]/div[2]/button").click()
time.sleep(10)
driver.save_screenshot('out.png');
driver.quit()

#print( "- Shaving and trimming" )
#cmd = "convert '%s' -shave 300x300 '%s'" % (dest,dest)
#os.system( cmd )
#cmd = "convert '%s' -fuzz 10%% -trim +repage '%s'" % (dest,dest)
#os.system( cmd )
