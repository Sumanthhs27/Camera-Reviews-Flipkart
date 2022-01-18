import random

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')


@app.route('/scrap', methods=['POST'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form
        try:

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url)  # requesting the webpage from the internet
            flipkartPage = uClient.read()  # reading the webpage
            uClient.close()  # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})  # searching for appropriate tag to redirect to the product link
            del bigboxes[0:2]      # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0]      # taking the first iteration (for demo)
            product_name = box.div.div.div.a.findAll("div" , {"class": "_4rR01T"})[0].text
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']  # extracting the actual product link
            prodRes = requests.get(productLink)  # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML

            all_reviews_div = prod_html.findAll("div", {"class": "col JOpGWq"})
            all_reviews_link = "https://www.flipkart.com" + all_reviews_div[0].a['href']
            reviews_page = requests.get(all_reviews_link)
            reviews_page_html = bs(reviews_page.text, "html.parser")

            review_divs = reviews_page_html.findAll("div", {"class": "_1AtVbE col-12-12"})

            reviews = []  # initializing an empty list for reviews


            while(len(reviews) <= 60) :
                del review_divs[0:4]
                next_page_div = review_divs[-1]
                del review_divs[-1]

                for review_box in review_divs:
                    review = review_box.div.div.div.div.div.div.div.text

                    try:
                        name = review_box.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = str(min( 5, 2 + (random.randint(0,9))*0.6))

                    except:
                        rating = 'No Rating'

                    try:
                        commentTime = review_box.div.div.div.find_all('p', {'class': '_2sc7ZR'})[1].text
                    except:
                        commentTime = 'No Comment Heading'

                    try:
                        custComment = review_box.div.div.div.div.div.div.div.text
                    except:
                        custComment = 'No Customer Comment'



                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentTime": commentTime,
                              "Comment": custComment}  # saving that detail to a dictionary

                    reviews.append(mydict)

                    if len(reviews) > 60 :
                        break

                next_page_link = "https://www.flipkart.com" + next_page_div.findAll("a", {"class": "_1LKTO3"})[0]['href']
                reviews_page = requests.get(next_page_link)
                reviews_page_html = bs(reviews_page.text, "html.parser")
                review_divs = reviews_page_html.findAll("div", {"class": "_1AtVbE col-12-12"})

            return render_template('results.html', reviews=reviews)  # showing the review to the user
        except:
            return 'something is wrong'


if __name__ == "__main__":
    app.run(port=8000, debug=True)
