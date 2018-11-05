import re
from bs4 import BeautifulSoup
import requests
from bs4 import SoupStrainer
from selenium import webdriver
from time import sleep, time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import networkx as nx
from datetime import datetime
from sys import argv
import csv
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


userset = set()
def source_to_soup(page_source):
	"""
	takes in page source, removes br tags and makes a Beautiful Soup object
	"""
	page_source = re.sub('<br>', '', page_source)
	page_source = re.sub('<br/', '', page_source)
	page_source = re.sub('<br />', '', page_source)
	return BeautifulSoup(page_source, 'html.parser', parse_only=SoupStrainer('div'))
def init_chromedriver():
	"""
	Initializes the chromedriver to not to load images
	:return: A chromedriver object
	"""
	chrome_options = webdriver.ChromeOptions()
	prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_settings.state.flash": 0}
	chrome_options.add_experimental_option("prefs", prefs)
	return webdriver.Chrome('./chromedriver', chrome_options=chrome_options)

def get_source(driver):
	"""
	Returns the page source - waits until it detects <html> tag
	:param driver:
	:return: the page source
	"""
	sleep(5)
	while True:
		source = driver.page_source
		if '<html' in source:
			return source
		else:
			print('Waiting for page to load')
			sleep(5)


def element_present(driver, sel):
	try:
		driver.find_element_by_css_selector(sel)
		return True
	except (NoSuchElementException, StaleElementReferenceException,TimeoutException):
		return False

def check_file(filename):
	contents = None
	try:
		with open(path, 'r', encoding='utf-8') as f:
			contents = f.read()
	except FileNotFoundError:
		print('File not in cache, loading the page')
	return contents

def get_reviews(rest_link):
	"""
	Get all the reviews of a restaurant
	:return: List of Review objects
	"""
	filename = rest_link.split('/')[-1]

	contents = None

	if contents is None:
		start = time()
		driver = init_chromedriver()
		# driver = init_firefox()
		driver.get(rest_link + '/reviews')
		# print('There are {} reviews'.format(self.review_count))
		# click on the button 'All reviews'
		sleep(5)
		driver.execute_script("window.scrollBy(0, 950);")
		while(1):
			try:
				el = driver.find_element_by_css_selector('#selectors > a.item.default-section-title.everyone.empty')
				webdriver.ActionChains(driver).move_to_element(el).click(el).perform()
			except TimeoutException:
				continue		
			except (NoSuchElementException):
				break
			break

		sleep(5)	
		load_more = '#reviews-container > div.notifications-content > div.res-reviews-container.res-reviews-area > div > div > div.mt0.ui.segment.res-page-load-more.zs-load-more > div.load-more.bold.ttupper.tac.cursor-pointer.fontsize2'
		sleep(5)
		while element_present(driver, load_more):
			try:
				el2 = driver.find_element_by_css_selector(load_more)
				driver.execute_script("return arguments[0].scrollIntoView();", el2)
				driver.execute_script("window.scrollBy(0, -150);")
				sleep(0.5)
				webdriver.ActionChains(driver).move_to_element(el2).click(el2).perform()
			except TimeoutException:
				continue
			except (StaleElementReferenceException, NoSuchElementException):
				break

		source = get_source(driver)
		driver.quit()
		#print(source)
		#write_to_file(source, filename, 1)  # 1 for Resto
		#print('{} reviews are loaded in {} secs'.format(self.review_count, time() - start))

	else:
		print('Using cached page')
		source = contents

	soup = source_to_soup(source)
	#review_blocks = soup.find_all('div', class_=re.compile('ui segments res-review-body'))

	review_blocks = (soup.find_all('div', class_='ui segment clearfix  brtop '))
	if len(review_blocks) == 0:
		print('Error in parsing reviews...\n Review blocks size is 0\n')
		with open('not_parsed','a+') as f:
			f.write(rest_link)
		return
	print('Loaded {} reviews'.format(len(review_blocks)))


	'''with open('reviews_csv_all', 'a', encoding='utf-8') as f:

	    spamwriter = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
		# spamwriter.writerow(
		#     [r.entity_id, r.name, r.rating, r.number_of_ratings, r.review_count, r.cuisines, r.link,
		#      r.cost_for_two])'''
	lastreview = filename + '_last'

	with open(filename,'a+', encoding='utf-8') as f:

		reviews = []
		i = start
		my_str = None
		for review in review_blocks[:]:
			try:
				name_and_link = review.find('div', class_='header nowrap ui left')
				# print(name_and_link.contents)
				u_link = name_and_link.contents[1].attrs['href']
				u_entity_id = int(name_and_link.contents[1].attrs['data-entity_id'])
				u_name = name_and_link.contents[1].contents[0].strip()
				# print(u_name)
				tup = (u_name,u_entity_id)
				#userset.add(tup)
				userset.add(u_link)			
				rating_and_rev_text = review.find('div', text='Rated')
				comment_time = review.find('time').attrs['datetime']
				rating = float(rating_and_rev_text.attrs['aria-label'].split()[-1])
				review_text = rating_and_rev_text.parent.contents[2].strip()
				#f.write('Review number '+str(my_ctr)+'\n')
				if my_str is None:
					my_str=comment_time
				f.write(str(comment_time)+'\n')
				f.write(u_name+'\n')
				f.write(str(u_entity_id)+'\n')
				f.write(str(rating)+'\n')
				f.write(review_text+'\n\n##\n\n')
				comm_file = filename + 'last_review_date'
				with open (comm_file,'w') as myfile200:
					myfile200.write(my_str)
				#f.write()
				#f.write()
				#			print()
				#r = Review()
				# r.user = User(u_link, u_entity_id)
				# if r.user.name is None:
				#     print('Invalid review, skipping')
				#     continue
				# r.user_link = u_link
				#
				#r.restaurant = self
				#r.time = review.find('time').attrs['datetime']
				#r.rating = float(rating_and_rev_text.attrs['aria-label'].split()[-1])
				# r.review_text = rating_and_rev_text.parent.contents[2].strip()
				#reviews.append(r)
				#
				# print(f'{i + 1} {u_name}', end=' ')
				# # f.write('{} | {} | {} | {} | {} | {}\n'.format(self.name, self.entity_id, r.user.name, r.user.entity_id, r.rating, r.time))
				# # f.write('{} | {} | {} | {}\n'.format(r.user.name, r.user.entity_id, r.user.followers_count, r.user.reviews_count))
				#spamwriter.writerow([self.name, self.entity_id, u_name, u_entity_id, u_link, r.rating, r.time]) #, r.review_text])
				#i += 1
			except:
				pass
			i += 1
		# # print()
		#return reviews



def extract_link(url):
	"""
	Creates a BeautifulSoup object from the link
	:param url: the link
	:return: a BeautifulSoup object equivalent of the url
	"""
	headers = {"Host": "www.zomato.com",
	       "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
	       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	       "Accept-Language": "en-US,en;q=0.5",
	       "Accept-Encoding": "gzip, deflate, br",
	       "Referer": "https://www.zomato.com/",
	       "Connection": "keep-alive"}

	if url.startswith('file'):
		with open(url.replace('file:\\\\', ''), encoding='utf-8') as fp:
	    		page_source = fp.read()

	else:
		r = requests.get(url, headers=headers)
		if r.status_code == 404:
			return None
		page_source = r.text

	page_source = re.sub('<br>', '', page_source)
	page_source = re.sub('<br />', '', page_source)
	page_source = re.sub('<br/>', '', page_source)
	soup = BeautifulSoup(page_source, 'html.parser')

	return soup

def get_restaurant_from_page(restaurant_card):
	'''
	link, name, entity_id, cuisines, review_count, geo_loc, rating, number_of_rating, cost_for_two

	:param restaurant_card:
	:return:
	'''
	try:

		name = restaurant_card.find('a', class_=re.compile('result-title hover_feedback zred bold ln24')).contents[0].strip()
		link = restaurant_card.find('a', class_=re.compile('result-title hover_feedback zred bold ln24')).attrs['href'].strip()
		entity_id = int(restaurant_card.find('div', class_=re.compile('js-search-result-li even')).attrs['data-res_id'])
		cost_for_two = int(restaurant_card.find('span', class_=re.compile('col-s-11 col-m-12 pl0')).contents[0].strip()[1: ].replace(',', ''))
		print(name)
		print(link)
		print(entity_id)
		print(cost_for_two)
		cuisines = restaurant_card.find('span', class_=re.compile('col-s-11 col-m-12 nowrap '))

		list_of_cuisines = []
		for cuisine in cuisines.contents:
			if len(cuisine) == 1:
				list_of_cuisines.append(cuisine.attrs['title'].strip())

		cuisines = ','.join(list_of_cuisines)
		rating = float(restaurant_card.find('div', class_=re.compile('rating-popup rating')).contents[0].strip())
		number_of_ratings = int(restaurant_card.find('span', class_=re.compile('rating-votes-div')).contents[0].split()[0])
		review_count = int(restaurant_card.find('a', {'data-result-type': 'ResCard_Reviews'}).contents[0].split()[0])
		

	except:
		pass
	

def get_all_restaurants(link, csv_file):
	soup = extract_link(link)

	restaurant_cards = soup.find_all('div', class_=re.compile('card search-snippet-card'))
	#with open(rest_card,'w'encoding='utf-8') as f:
	#	f.write(restaurant_cards.text)
	#print(len(restaurant_cards))


	with open(csv_file,'a', encoding='utf-8') as f:
		for restaurant_card in restaurant_cards:
			link = restaurant_card.find('a', class_=re.compile('result-title hover_feedback zred bold ln24')).attrs['href']
			#get_restaurant_from_page(restaurant_card)
			print(link)
			f.write(link+'\n')
			'''spamwriter.writerow([r.entity_id, r.name, r.rating, r.number_of_ratings, r.review_count, r.cuisines, r.link, r.cost_for_two])
	return urls'''

def get_all_resto_driver():
	csv_file = 'restaurant_info_kolkata'
	# with open(csv_file, 'w') as csvfile:
	#     spamwriter = csv.writer(csvfile,
	#                             quoting=csv.QUOTE_NONNUMERIC)
	#     spamwriter.writerow(['R+++est_id', 'Rest_name', 'Rating', 'Number_of_ratings', 'Reviews', 'Cuisines', 'Link', 'Cost_for_two'])

	#
	link = 'https://www.zomato.com/kolkata/restaurants?page='
	for i in range(1, 282):
		print('Page: {}'.format(i))
		get_all_restaurants(link + str(i), csv_file)

def test_review():

	urls = []
	with open ('skip_lines', "r") as myfile:
		skip = int(myfile.readline()) 
	with open ('restaurant_info_kolkata', "r") as myfile:
		for skiplines in range(skip):
			skiptext = myfile.readline()
		for line in myfile.readlines():
			print(line)
			skip = skip + 1
			get_reviews(line)
			with open ('user_links', "a") as myfile2:
				for item in userset:
					myfile2.write(item+'\n')
			userset.clear()
			with open ('skip_lines', "w") as myfile1:
				myfile1.write(str(skip))
			
	
	'''with open('restaurant_info_kolkata','r', encoding='utf-8') as f:
		resto_reader = f.read()
		for row in resto_reader:
	   	 # print(row['Link'])
			urls.append(row)
			print(row)
	print(len(urls))
	j = len(urls)
	for i in range(0, j):
		url = 'https://www.zomato.com/kolkata/' + urls[i]
		print(url)
	'''
		#scrape comments

#get_all_resto_driver()
test_review()
#get_reviews('https://www.zomato.com/kolkata/aura-the-sky-bar-theatre-road')


