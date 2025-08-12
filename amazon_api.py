from amazon_paapi5 import AmazonApi

import os



AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")

AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")

AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")

AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")



def get_amazon_client():

    return AmazonApi(

        AMAZON_ACCESS_KEY,

        AMAZON_SECRET_KEY,

        AMAZON_ASSOCIATE_TAG,

        AMAZON_COUNTRY

    )

