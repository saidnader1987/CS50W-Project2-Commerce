# CS50W Project 2 - Commerce

This project is part of the Harvard University's CS50W course on Web Programming with Python and JavaScript. It's an implementation of an eBay-like e-commerce auction site that allows users to post auction listings, place bids on listings, comment on those listings, and add listings to a "watchlist", using Django, HTML, and CSS.

Video Demo: https://www.youtube.com/watch?v=eoBdxbHV0lk

## Description

This web application serves users to make and bid on auction listings. It offers functionalities to comment on listings and add them to a personal watchlist. The main features of the web application include:

- Posting auction listings
- Bidding on auction listings
- Commenting on auction listings
- Adding listings to a "watchlist"
- Viewing active listings and those specific to a category
- Closing auctions by the listing creator
- Viewing and managing all listings, comments, and bids through Django's admin interface

For detailed project requirements, refer to the project specifications on the CS50W course website [here](https://cs50.harvard.edu/web/2020/projects/2/commerce/).

## Getting Started

To run this project locally, you need Python and pip installed on your system. If you don't have Python and pip installed, visit the [official Python website](https://www.python.org/downloads/) and follow the instructions there.

A database is included in the repository for immediate use. If you wish to start with a fresh database, remember to make migrations after deleting the existing one.

1. **Install the dependencies**

```
pip install -r requirements.txt
```

2. **Run the migrations (if you deleted the existing database)**

```
python manage.py makemigrations auctions
python manage.py migrate
```

3. **Run the application**

```
python manage.py runserver
```

Then, open your browser and visit `http://localhost:8000` to see the application in action.

## Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.
