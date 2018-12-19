# coding=utf-8

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

# (c) Jani Suoranta Dec/2018
# This program scrapes the open positions at
# Tampereen kaupunki, finds  keyword matching positions and 
# sends them to your email using GMAIL SMTP server.

# SETTING UP IN 6 STEPS #
# 1. Install python3 and the dependencies listed at LINKKI.
# 2. Create an empty .txt file. 
# 	 Add its directory $PATH below. For example '/Users/User/Documents/scraper/log.txt'
FULL_TXT_LOG_FILE_PATH = ''
# 3. Insert keyword for the open positions you're interested in below in lowercase.
# 	 For example: 'ohjaaja'
KEYWORD = ''
# 4. Add FROM email credentials to 'FROM_ACCOUNT_NAME' and 'FROM_ACCOUNT_PASSWORD' below.
# 	 For example 'sender@gmail.com' and password as it is.
FROM_ACCOUNT_NAME = ''
FROM_ACCOUNT_PASSWORD = ''
# 5. Add RECIPIENT email below. For example 'recipient@gmail.com'
RECIPIENT_ACCOUNT_NAME = ''
# 6. Test the script with different keywords and profit.

# Problems with GMAIL credentials? See these threads for help:
# https://support.google.com/mail/answer/7126229
# https://support.google.com/accounts/answer/6010255

# Function from https://realpython.com/python-web-scraping-practical-introduction/ by Colin OKeefe
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML,
    return the text content, otherwise return None.
    URL: https://www.tampere.fi/tyo/tyonhakijalle/avoimet-tyopaikat.html
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


# Function from https://realpython.com/python-web-scraping-practical-introduction/ by Colin OKeefe
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
       		and content_type is not None
        	and content_type.find('html') > -1)


# Function from https://realpython.com/python-web-scraping-practical-introduction/ by Colin OKeefe
def log_error(e):
    """
    Return error.
    """
    return "Error with GET: " + (e)


# Let's get to the bone
""" Get "open positions" page's HTML from Tampere.fi """
raw_html = simple_get("https://www.tampere.fi/tyo/tyonhakijalle/avoimet-tyopaikat.html")

""" Parse through the HTML and pick div's that are open positions """
html = BeautifulSoup(raw_html, 'html.parser')
mydivs = html.find_all("div", class_="col-xs-12 col-md-12 col-sm-12 result")
for div in mydivs:
	""" Take the text in the div's <a> element """
	openPosition = div.find("a").text
	""" Look for the keyword in the HTML case insensitively """
	if openPosition.lower().__contains__(KEYWORD):
		""" Get the link to the open position """
		link = div.find("a")['href']
		""" Attach the needed beginning to the URL """
		link = "https://www.tampere.fi" + link

		""" Check the log if this job has been mailed already """
		fileRead = open(FULL_TXT_LOG_FILE_PATH, 'r')
		sentPosition = 'no'

		""" Check each line of the file for matches with the current openPosition. """
		for line in fileRead:
			""" If this position has been mailed already """
			if line.__contains__(link):
				sentPosition = link

		""" If the position has been mailed already """
		if sentPosition == link:
			fileRead.close()
		""" If not, create and send the mail """
		if sentPosition != link:
			fileRead.close()
			# Insert your prefered email text here
			""" Add the text for a new open position """
			newJobAvailable = "Hey recipient!\n\nTampere city has a new open position:\n\n" + openPosition + "\n\n" + link + "\n\n\n" + "Greetings,\nYou"
			
			""" Send e-mail if a proper job position was found """
			import smtplib
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.ehlo()
			server.starttls()
			server.ehlo()
			# Insert FROM email login credentials below thrice. Add RECIPIENT address twice.
			server.login(FROM_ACCOUNT_NAME, FROM_ACCOUNT_PASSWORD)

			msg = "\r\n".join(["From: " + FROM_ACCOUNT_NAME,
							"To: " + RECIPIENT_ACCOUNT_NAME,
							"Subject: Tampere city OPEN JOB POSITION",
  							"",
 							newJobAvailable
 							])
  
			""" Send the mail """
			server.sendmail(FROM_ACCOUNT_NAME, RECIPIENT_ACCOUNT_NAME, msg.encode('utf-8'))
			server.close()

			""" Append the url to the log to avoid duplicate emailing """
			fileWrite = open(FULL_TXT_LOG_FILE_PATH, 'a')
			fileWrite.write(link + '\n')
			fileWrite.close()