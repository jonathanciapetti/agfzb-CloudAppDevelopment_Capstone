import datetime
from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    name = models.CharField(null=False, max_length=50)
    description = models.CharField(null=True, max_length=500)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=50)
    dealer_id = models.IntegerField(null=True)

    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    SPORT = "Sport"
    COUPE = "Coupe"
    MINIVAN = "Mini"
    VAN = "Van"
    PICKUP = "Pickup"
    TRUCK = "Truck"
    BIKE = "Bike"
    SCOOTER = "Scooter"
    OTHER = "Other"
    CAR_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Station wagon"),
        (SPORT, "Sports Car"),
        (COUPE, "Coupe"),
        (MINIVAN, "Mini van"),
        (VAN, "Van"),
        (PICKUP, "Pick-up truck"),
        (TRUCK, "Truck"),
        (BIKE, "Motor bike"),
        (SCOOTER, "Scooter"),
        (OTHER, 'Other')
    ]

    model_type = models.CharField(
        null=False,
        max_length=15,
        choices=CAR_CHOICES,
        default=SEDAN)

    YEAR_CHOICES = []
    for r in range(
            1969,
            (datetime.datetime.now().year + 1)
    ):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        ('year'),
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year
    )

    def __str__(self):
        return f"""{self.name}, {str(self.year)}, {self.model_type}"""


class CarDealer:
    def __init__(
            self,
            address,
            city, full_name,
            id,
            lat,
            long,
            short_name,
            st,
            state,
            zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.state = state
        self.zip = zip
        self.idx = 0

    def __str__(self):
        return f"""{self.full_name}, {self.state}"""


class DealerReview:
    def __init__(self, dealership, id, name, purchase, review, car_make=None, car_model=None, car_year=None,
                 purchase_date=None, sentiment="neutral"):
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.dealership = dealership
        self.id = id
        self.name = name
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.review = review
        self.sentiment = sentiment

    def __str__(self):
        return f"""Reviewer: {self.name} Review: {self.review}"""
