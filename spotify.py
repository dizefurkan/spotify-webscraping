from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.keys import Keys
from time import sleep
import unittest
import requests
import json

class Spotify(unittest.TestCase):
  def setUp(self):
    chromeDriver = r'D:\Git\spotify-webscraping\chromedriver.exe'
    self.driver = webdriver.Chrome(chromeDriver)
    self.baseUrl = 'https://open.spotify.com'
  
  def login(self):
    driver = self.driver
    driver.get(self.baseUrl)
    sleep(1)
    driver.find_element_by_id('has-account').click()
    sleep(2)
    username = input('Username: ')
    password = input('Password: ')
    driver.find_element_by_id('login-username').send_keys(username)
    driver.find_element_by_id('login-password').send_keys(password)
    driver.find_element_by_id('login-button').click()
    sleep(2)
    self.currentUrl = driver.current_url

  def test_playlists(self):
    self.login()
    driver = self.driver
    link = 'https://open.spotify.com/collection/playlists'
    driver.get(link)
    lastHeight = driver.execute_script('return document.body.scrollHeight')
    while True:
      driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
      newHeight = driver.execute_script('return document.body.scrollHeight')
      sleep(1)
      if lastHeight == newHeight:
        break
      lastHeight = newHeight
    soup = BS(driver.page_source, 'html.parser')
    playlistItem = soup.find_all(attrs={'class':'media-object'})
    for item in playlistItem:
      title = item.find(attrs={'class':'mo-info-name'})
      print('Title: {}\nLink: {}'.format(
        title.text,
        title['href']
      ))
      url = title['href']
      self.innerPlaylist(url)

  def replace_text(self, word):
    while True:
      word = word.replace('-', '')
      word = word.replace(',', '')
      word = word.replace('-', '')
      if '-' not in word:
        word = word.replace("'", '-')
        word = word.replace('/', '-')
        word = word.replace(' ', '-')
        break
    return word
  def innerPlaylist(self, url):
    driver = self.driver
    driver.get(self.baseUrl + url)
    sleep(2)
    soup = BS(driver.page_source, 'html.parser')
    row = soup.find_all(attrs={'class':'tracklist-row'})
    meta = soup.find('div', attrs={'class':'entity-name'})
    title = meta.find('h2').text
    title = self.replace_text(title)
    fileName = title.lower() + '.json'
    list = []
    for item in row:
      songName = item.find(attrs={'class':'tracklist-name'})
      songAlbum = item.find_all(attrs={'class':'link-subtle'})
      artists = []
      for meta in songAlbum:
        item = meta.text
        artists.append(item)
      item = {
        'title': songName.text,
        'artist': artists
      }
      list.append(item)
    with open(fileName, 'a+', encoding='utf-8') as fo:
      json.dump(list, fo, ensure_ascii=False)
    fo.close()
if __name__ == '__main__':
  unittest.main()