import requests
import json
import os
from dotenv import load_dotenv
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

load_dotenv()

# Function for making HTTP GET requests
def get_request(url, api_key=False, **kwargs):
    try:
        if api_key:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs,
                auth=HTTPBasicAuth('apikey', api_key)
            )
        else:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs
            )
    except Exception as ex:
        print(ex)
        return 500
    else:
        print(response.status_code)
        if 199 < response.status_code < 300:
            if response.text:
                return json.loads(response.text)
        else:
            return response.status_code


# Function for making HTTP POST requests
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except Exception as ex:
        print(ex)
        return 500
    else:
        return response


# Gets all dealers from the Cloudant DB with the Cloud Function get-dealerships
def get_dealers_from_cf(url):
    json_result = get_request(url)
    dealers = json_result["body"]["rows"]
    output = []

    for dealer in dealers:
        output.append(CarDealer(
            id=dealer["doc"]["id"],
            address=dealer["doc"]["address"],
            city=dealer["doc"]["city"],
            full_name=dealer["doc"]["full_name"],
            lat=dealer["doc"]["lat"],
            long=dealer["doc"]["long"],
            short_name=dealer["doc"]["short_name"],
            st=dealer["doc"]["st"],
            state=dealer["doc"]["state"],
            zip=dealer["doc"]["zip"]
        ))

    return output


def get_dealer_by_id(url, dealer_id):
    json_result = get_request(url, dealerId=dealer_id)
    return CarDealer(
        address=json_result["entries"][0]["address"],
        city=json_result["entries"][0]["city"],
        full_name=json_result["entries"][0]["full_name"],
        id=json_result["entries"][0]["id"],
        lat=json_result["entries"][0]["lat"],
        long=json_result["entries"][0]["long"],
        short_name=json_result["entries"][0]["short_name"],
        st=json_result["entries"][0]["st"],
        state=json_result["entries"][0]["state"],
        zip=json_result["entries"][0]["zip"]
    )


def get_dealers_by_state(url, state):
    json_result = get_request(url, state=state)
    dealers = json_result["body"]["docs"]
    output = []

    for dealer in dealers:
        output.append(CarDealer(
            address=dealer["address"],
            city=dealer["city"],
            full_name=dealer["full_name"],
            id=dealer["id"],
            lat=dealer["lat"],
            long=dealer["long"],
            short_name=dealer["short_name"],
            st=dealer["st"],
            state=dealer["state"],
            zip=dealer["zip"]))

    return output


def get_dealer_reviews_from_cf(url, dealer_id):
    json_result = get_request(url, dealerId=dealer_id)
    output = []

    if json_result:
        reviews = json_result["entries"]
        for review in reviews:
            try:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    id=review["id"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    purchase_date=review["purchase_date"]
                )

            except KeyError as key_error:
                print(key_error)
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    id=review["id"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                )

            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            if review_obj.sentiment is None:
                review_obj.sentiment = "neutral"
            output.append(review_obj)

    return output


def analyze_review_sentiments(review_text):

    url = os.getenv('WATSON_NLU_URL')
    api_key = os.getenv("WATSON_NLU_API_KEY")

    version = '2021-08-01'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)

    try:
        response = nlu.analyze(
            text=review_text,
            features=Features(sentiment=SentimentOptions())
        ).get_result()
        sentiment_label = response["sentiment"]["document"]["label"]
    except Exception as ex:
        print(ex)
    else:
        return sentiment_label
