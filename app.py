#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# [DONE] TODO: connect to a local postgresql database
# DB connection configuration is implemented in config.py

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Shows Table: To links between venues and artists


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.DateTime)

# show = db.Table('show',
#   db.Column('venue_id', db.Integer, db.ForeignKey('venue.id')),
#   db.Column('artist_id', db.Integer, db.ForeignKey('artist.id')),
#   db.Column('start_time', db.DateTime)
# )


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(500)))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues', lazy=True)
    # artist = db.relationship('Artist', secondary=show, backref=db.backref('venues', lazy=True))
    # artist = db.relationship('Artist', backref='venues', lazy=True)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True)
    # venues = db.relationship('Venue', secondary=show, backref=db.backref('artists', lazy=True))

    # [DONE] TODO: implement any missing fields, as a database migration using Flask-Migrate

# [DONE] TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # [DONE] TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    
    # data = Venue.query.all()
    venues = Venue.query.all()

    data = []
    city_state_venue = []

    for venue in venues:
        location_based_venues = db.session.query(Venue).filter_by(
            city=venue.city).all()
        for city_venue in location_based_venues:
            city_state_venue.append({
                'id': city_venue.id,
                'name': city_venue.name,
                'num_upcoming_shows': len(db.session.query(Venue).join(Show).filter(city_venue.id  == Show.venue_id).filter(Show.start_time > datetime.now()).all())
            })
            # show.query.filter_by(show.venue_id == city_venue.id).filter_by(show.start_time >= datetime.now()).all()

            data.append({
                'city': venue.city,
                'state': venue.state,
                'venues': city_state_venue
            })

    # data=[{
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #   }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #   }]
    # }, {
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # [DONE] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    data = []

    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    for search_result in search_results:
        data.append({
            'id': search_result.id,
            'name': search_result.name,
            'num_upcoming_shows': len(Show.query.filter(Show.venue_id == search_result.id).filter(Show.start_time > datetime.now()).all())
        })

    response = {
        'count': len(search_results),
        'data': data
    }
    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # [DONE] TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)

    if not venue:
        return redirect(url_for('not_found_errors'))

    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_list = []
    past_shows_list = []

    for upcoming_show in upcoming_shows:
        upcoming_shows_list.append({
            'artist_id': upcoming_show.artist_id,
            'artist_name': upcoming_show.artist.name,
            'artist_image_link': upcoming_show.artist.image_link,
            'start_time': upcoming_show.start_time
        })

    for past_show in past_shows:
        past_shows_list.append({
            'artist_id': past_show.artist_id,
            'artist_name': past_show.artist.name,
            'artist_image_link': past_show.artist.image_link,
            'start_time': past_show.start_time
        })

    data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "image_link": venue.image_link,
            "past_shows": past_shows_list,
            "upcoming_shows": upcoming_shows_list,
            "past_shows_count": len(past_shows_list),
            "upcoming_shows_count": len(upcoming_shows_list),
        }

    # data1={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "past_shows": [{
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "genres": ["Classical", "R&B", "Hip-Hop"],
    #   "address": "335 Delancey Street",
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "914-003-1132",
    #   "website": "https://www.theduelingpianos.com",
    #   "facebook_link": "https://www.facebook.com/theduelingpianos",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 3,
    #   "name": "Park Square Live Music & Coffee",
    #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #   "address": "34 Whiskey Moore Ave",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "415-000-1234",
    #   "website": "https://www.parksquarelivemusicandcoffee.com",
    #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "past_shows": [{
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [{
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # [DONE] TODO: insert form data as a new Venue record in the db, instead
    # [DONE] TODO: modify data to be the data object returned from db insertion

    error = False

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        website = request.form['website']
        facebook_link = request.form['facebook_link']
        # as genres is stored as an array in db
        genres = request.form.getlist('genres')
        if 'seeking_talent' in request.form:
            seeking_talent = True
        else:
            seeking_talent = False
        seeking_description = request.form['seeking_description']

        venue = Venue(name=name,
                      city=city,
                      state=state,
                      address=address,
                      phone=phone,
                      genres=genres,
                      website=website,
                      image_link=image_link,
                      facebook_link=facebook_link,
                      seeking_talent=seeking_talent,
                      seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        # [DONE] TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    if error:
        flash('Error: Venue ' + request.form['name'] + ' could not be listed!')
        # on successful db insert, flash success
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # [DONE] TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    error = False

    try:
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('Error: Venue ' +
              request.form['name'] + ' could not be deleted!')
    # on successful db insert, flash success
    else:
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')

    return render_template('pages/home.html')
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # [DONE] TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    # data=[{
    #   "id": 4,
    #   "name": "Guns N Petals",
    # }, {
    #   "id": 5,
    #   "name": "Matt Quevedo",
    # }, {
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # [DONE] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    data = []

    search_term = request.form.get('search_term', '')
    search_results = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    for search_result in search_results:
        data.append({
            'id': search_result.id,
            'name': search_result.name,
            'num_upcoming_shows': len(Show.query.filter(Show.artist_id == search_result.id).filter(Show.start_time > datetime.now()).all())
        })

    response = {
        'count': len(search_results),
        'data': data
    }

    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "num_upcoming_shows": 0,
    #   }]
    # }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # [DONE] TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)

    if not artist:
        return redirect(url_for('not_found_errors'))

    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_list = []
    past_shows_list = []

    for upcoming_show in upcoming_shows:
        upcoming_shows_list.append({
            'venue_id': upcoming_show.venue_id,
            'venue_name': upcoming_show.venue.name,
            'venue_image_link': upcoming_show.venue.image_link,
            'start_time': upcoming_show.start_time
        })

    for past_show in past_shows:
        past_shows_list.append({
            'venue_id': past_show.venue_id,
            'venue_name': past_show.venue.name,
            'venue_image_link': past_show.venue.image_link,
            'start_time': past_show.start_time
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list)
        }

    # data1={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "past_shows": [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 5,
    #   "name": "Matt Quevedo",
    #   "genres": ["Jazz"],
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "300-400-5000",
    #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "past_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    #   "genres": ["Jazz", "Classical"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "432-325-5432",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    # artist = {
    #   "name": form.name.data,
    #   "city": form.city.data,
    #   "state": form.state.data,
    #   "phone": form.phone.data,
    #   "genres": form.genres.data,
    #   # "website": form.website.data,
    #   "image_link": form.image_link.data,
    #   "facebook_link": form.facebook_link.data,
    #   "seeking_venue": form.seeking_venue.data,
    #   "seeking_description": form.seeking_description.data
    # }

    # artist = {
    #   form.name.data: artist.name,
    #   form.city.data: artist.city,
    #   form.state.data: artist.state,
    #   form.phone.data: artist.phone,
    #   form.genres.data: artist.genres,
    #   # form.website.data: artist.website,
    #   form.image_link.data: artist.image_link,
    #   form.facebook_link.data: artist.facebook_link,
    #   form.seeking_venue.data: artist.seeking_venue,
    #   form.seeking_description.data: artist.seeking_description
    # }

    if artist:
        form.name.data: artist.name  # request.form['name'].data
        form.city.data: artist.city
        form.state.data: artist.state
        form.phone.data: artist.phone
        form.genres.data: artist.genres
        form.website.data: artist.website
        form.image_link.data: artist.image_link
        form.facebook_link.data: artist.facebook_link
        form.seeking_venue.data: artist.seeking_venue
        form.seeking_description.data: artist.seeking_description

    # artist={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # [DONE] TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # [DONE] TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False
    artist = Artist.query.get(artist_id)

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        # as genres is stored as an array in db
        artist.genres = request.form.getlist('genres')
        artist.website = request.form['website']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        if 'seeking_venue' in request.form:
            artist.seeking_venue = True
        else:
            artist.seeking_venue = False
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('Error: Artist ' +
              request.form['name'] + ' could not be edited!')
    else:
        flash('Artist ' + request.form['name'] + ' is edited successfully!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data: venue.name  # request.form['name'].data
        form.city.data: venue.city
        form.state.data: venue.state
        form.phone.data: venue.phone
        form.address.data: venue.address
        form.genres.data: venue.genres
        form.website.data: venue.website
        form.image_link.data: venue.image_link
        form.facebook_link.data: venue.facebook_link
        form.seeking_talent.data: venue.seeking_talent
        form.seeking_description.data: venue.seeking_description
    # venue={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # [DONE] TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # [DONE] TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue = Venue.query.get(venue_id)

    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        # as genres is stored as an array in db
        venue.genres = request.form.getlist('genres')
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        if 'seeking_talent' in request.form:
            artist.seeking_talent = True
        else:
            artist.seeking_talent = False
        artist.seeking_description = request.form['seeking_description']
    finally:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # [DONE] TODO: insert form data as a new Venue record in the db, instead
    # [DONE] TODO: modify data to be the data object returned from db insertion

    error = False

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        if 'seeking_venue' in request.form:
            seeking_venue = True
        else:
            seeking_venue = False
        artist.seeking_description = request.form['seeking_description']

        artist = Artist(name=name,
                        city=city,
                        state=state,
                        phone=phone,
                        genres=genres,
                        website=website,
                        image_link=image_link,
                        facebook_link=facebook_link,
                        seeking_venue=seeking_venue,
                        seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('Error: Artist ' +
              request.form['name'] + ' could not be listed!')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    # [DONE] TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # [DONE] TODO: replace with real venues data.

    shows = db.session.query(Show).join(Artist).join(Venue).all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time
        })

    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # [DONE] TODO: insert form data as a new Show record in the db, instead

    error = True

    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_name,
                    venue_id=venue_id, start_time=start_times)

        db.session.add(show)
        db.session.close()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('Error: Show could not be listed!')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    # [DONE] TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
