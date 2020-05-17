#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import * #imported db Models

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# In a dedicate models.py file. Imported here

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    """
    Formats date and time associated with db models

    Args:
        value,
        format: with option of full and medium formats -> defaults to 'medium'
        -----
        full format: EEEE MMMM, d, y 'at' h:mma
        medium format: EE MM, dd, y h:mma

    Returns:
        formatted date and time
    """
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
    """
    Routes the user to the homepage
    
    Args:
        None

    Returns:
        homepage from pages/
    """
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    """
    Displays list of venues for each city, state

    Args:
        None

    Returns:
        list of venues for each city, state
    """
    venues = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    data = []

    for venue in venues:
        location_based_venues = Venue.query.filter(Venue.city == venue.city).filter(Venue.state == venue.state).all()

        data.append({
            'city': venue.city,
            'state': venue.state,
            'venues': location_based_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    """
    Search for venues

    Args:
        None

    Returns:
        searched venue
    """
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

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """
    Show specific venue

    Args:
        venue_id

    Returns:
        fetch and display specific venue
    """
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
            'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
        })

    for past_show in past_shows:
        past_shows_list.append({
            'artist_id': past_show.artist_id,
            'artist_name': past_show.artist.name,
            'artist_image_link': past_show.artist.image_link,
            'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
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

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    """
    Create a submission form for venues

    Args:
        None

    Returns:
        created page for venues submission form
    """
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    """
    Submit venue info to be posted 

    Args:
        None

    Returns:
        submitted venue info
    """
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
    if error:
        flash('Error: Venue ' + request.form['name'] + ' could not be listed!')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """
    Delete a specific venue

    Args:
        venue_id

    Returns:
        refreshed page with a the venue being deleted
    """
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
    else:
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    """
    Displays list of artists 

    Args:
        None

    Returns:
        list of venues for each city, state
    """
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    """
    Search for artists

    Args:
        None

    Returns:
        searched artist
    """
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

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    """
    Show specific artist

    Args:
        artist_id

    Returns:
        fetch and display specific artists
    """
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
            'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
        })

    for past_show in past_shows:
        past_shows_list.append({
            'venue_id': past_show.venue_id,
            'venue_name': past_show.venue.name,
            'venue_image_link': past_show.venue.image_link,
            'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
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

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """
    Create an edit form to edit specific artist info

    Args:
        artist_id

    Returns:
        fetch and display specific artist info to be editted
    """
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data: artist.name
        form.city.data: artist.city
        form.state.data: artist.state
        form.phone.data: artist.phone
        form.genres.data: artist.genres
        form.website.data: artist.website
        form.image_link.data: artist.image_link
        form.facebook_link.data: artist.facebook_link
        form.seeking_venue.data: artist.seeking_venue
        form.seeking_description.data: artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """
    Submit artist info to be posted after edit

    Args:
        artist_id

    Returns:
        edit submission of artist info
    """
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
    """
    Create an edit form to edit specific venue info

    Args:
        venue_id

    Returns:
        fetch and display specific venue info to be editted
    """
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data: venue.name
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

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    """
    Submit venue info to be posted after edit

    Args:
        venue_id

    Returns:
        edit submission of venue info
    """
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
    """
    Create a submission form for artists

    Args:
        None

    Returns:
        created page for artists submission form
    """
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """
    Submit artist info to be posted

    Args:
        None

    Returns:
        submitted artist info
    """
    error = False

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        website = request.form['website']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        if 'seeking_venue' in request.form:
            seeking_venue = True
        else:
            seeking_venue = False
        seeking_description = request.form['seeking_description']

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
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    """
    Displays list of artists shows in venues

    Args:
        None

    Returns:
        list of artists shows in venues
    """

    shows = db.session.query(Show).join(Artist).join(Venue).all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    """
    Create a submission form for shows

    Args:
        None

    Returns:
        created page for shows submission form
    """
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """
    Submit show info to be posted

    Args:
        None

    Returns:
        submitted show info
    """
    error = True

    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id,
                    venue_id=venue_id,
                    start_time=start_times)

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
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 error

    Args:
        error

    Returns:
        404 error page
    """
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """
    Handles 500 error

    Args:
        error

    Returns:
        500 error page
    """
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

# For default port (port=5432):
if __name__ == '__main__':
    app.run(debug=True)

# To specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
