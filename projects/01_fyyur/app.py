#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, make_response
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(), nullable=False)
    shows = db.relation('Show', backref='venue', lazy='select')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.split(','),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": [{
                "artist_id": s.artist_id,
                "artist_name": s.artist.name,
                "artist_image_link": s.artist.image_link,
                "start_time": str(s.start_time)
            } for s in self.shows if s.start_time < datetime.now()],
            "upcoming_shows": [{
                "artist_id": s.artist_id,
                "artist_name": s.artist.name,
                "artist_image_link": s.artist.image_link,
                "start_time": str(s.start_time)
            } for s in self.shows if s.start_time > datetime.now()],
            "past_shows_count": len([s for s in self.shows if s.start_time < datetime.now()]),
            "upcoming_shows_count": len([s for s in self.shows if s.start_time > datetime.now()]),
        }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    always_available = db.Column(db.Boolean(), nullable=False, default=True)
    shows = db.relation('Show', backref='artist', lazy='select')
    available_times = db.relation(
        'ArtistAvailableTimes', backref='artist', lazy='select')

    def is_available(self, time=datetime.now()):
        if self.always_available:
            return True

        for t in self.available_times:
            if t.availability_start < time and t.availability_end > time:
                return True

        return False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.split(','),
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": [{
                "venue_id": s.venue_id,
                "venue_name": s.venue.name,
                "venue_image_link": s.venue.image_link,
                "start_time": str(s.start_time)
            } for s in self.shows if s.start_time < datetime.now()],
            "upcoming_shows": [{
                "venue_id": s.venue_id,
                "venue_name": s.venue.name,
                "venue_image_link": s.venue.image_link,
                "start_time": str(s.start_time)
            } for s in self.shows if s.start_time > datetime.now()],
            "past_shows_count": len([s for s in self.shows if s.start_time < datetime.now()]),
            "upcoming_shows_count": len([s for s in self.shows if s.start_time > datetime.now()]),
            "available_times": self.available_times,
            "is_available": self.is_available()
        }


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "venue_id": self.venue_id,
            "venue_name": self.venue.name,
            "artist_id": self.artist_id,
            "artist_name": self.artist.name,
            "artist_image_link": self.artist.image_link,
            "start_time": str(self.start_time)
        }


class ArtistAvailableTimes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.ForeignKey('Artist.id'))
    availability_start = db.Column(db.DateTime, nullable=False)
    availability_end = db.Column(db.DateTime, nullable=False)

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
    artists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
    venues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
    return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.order_by('city').all()
    data_by_city = {}
    last_city = None
    for v in venues:
        if not f'{v.city},{v.state}' in data_by_city:
            data_by_city[f'{v.city},{v.state}'] = []
        data_by_city[f'{v.city},{v.state}'].append({
            'id': v.id,
            'name': v.name,
            'num_upcoming_shows': len([s for s in v.shows if s.start_time > datetime.now()])
        })

    data = [{
        "city": k.split(',')[0],
        "state": k.split(',')[1],
        "venues": v
    } for k, v in data_by_city.items()]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    term = request.form.get('search_term', '')
    result = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
    response = {
        "count": len(result),
        "data": [{
            'id': v.id,
            'name': v.name,
            'num_upcoming_shows': len([s for s in v.shows if s.start_time > datetime.now()])
        } for v in result]
    }
    return render_template('pages/search_venues.html', results=response, search_term=term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id).to_dict()
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form_data = request.form
    genres = form_data.getlist('genres')
    error = False
    data = Venue(name=form_data['name'], city=form_data['city'], state=form_data['state'], address=form_data['address'],
                 phone=form_data['phone'], genres=','.join(genres), facebook_link=form_data['facebook_link'])
    try:
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    result = Artist.query.all()
    data = [{
        "id": a.id,
        "name": a.name
    } for a in result]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term', '')
    result = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
    if ', ' in term:
        city_state_term = term.split(', ')
        city = city_state_term[0]
        state = city_state_term[1]
        if state.lower() in [state.value.lower() for state in State]:
            city_state_result = Artist.query.filter(Artist.state.ilike(f'{state}')).filter(Artist.city.ilike(f'{city}')).all()
            result = result + city_state_result
    response = {
        "count": len(result),
        "data": [{
            'id': a.id,
            'name': a.name,
            'num_upcoming_shows': len([s for s in a.shows if s.start_time > datetime.now()])
        } for a in result]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = artist.to_dict()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    form.genres.data = artist.genres.split(',')
    return render_template('forms/edit_artist.html', form=form, artist=artist.to_dict())


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    formData = request.form

    artist.name = formData['name']
    artist.city = formData['city']
    artist.state = formData['state']
    artist.phone = formData['phone']
    artist.genres = ','.join(formData.getlist('genres'))
    artist.facebook_link = formData['facebook_link']

    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/<int:artist_id>/availability/add', methods=['GET'])
def add_artist_availability(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistTimesForm()
    return render_template('forms/add_artist_availability.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/availability/add', methods=['POST'])
def add_artist_availability_submission(artist_id):
    artist = Artist.query.get(artist_id)
    start = request.form['availability_start']
    end = request.form['availability_end']
    artist.always_available = False
    new_artist_times = ArtistAvailableTimes(
        artist_id=artist.id, availability_start=start, availability_end=end)
    try:
        db.session.add(new_artist_times)
        db.session.commit()
    except:
        db.session.rollback()

    return redirect(url_for('show_artist', artist_id=artist.id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres.split(',')
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form_data = request.form

    venue.name = form_data['name']
    venue.city = form_data['city']
    venue.state = form_data['state']
    venue.address = form_data['address']
    venue.phone = form_data['phone']
    venue.genres = ','.join(form_data.getlist('genres'))
    venue.facebook_link = form_data['facebook_link']

    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form_data = request.form
    if form_data['is_always_available'] == 'yes':
        always_available = True
    else:
        always_available = False

    if form_data['is_seeking_venue'] == 'yes':
        seeking_venue = True
    else:
        seeking_venue = False
    data = Artist(name=form_data['name'], city=form_data['city'], state=form_data['state'], phone=form_data['phone'], genres=','.join(
        form_data.getlist('genres')), facebook_link=form_data['facebook_link'], image_link=form_data['image_link'], always_available=always_available,
        seeking_venue=seeking_venue)
    error = False
    try:
        db.session.add(data)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = [s.to_dict() for s in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form_data = request.form
    start_time = form_data['start_time']
    venue_id = form_data['venue_id']

    artist_id = form_data['artist_id']
    artist = Artist.query.get(artist_id)

    time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    if not artist.is_available(time):
        flash(
            "The artist is not available at the selected time. Please select another time")
        form = ShowForm(artist_id=artist_id,
                        venue_id=venue_id, start_time=time)
        return render_template('forms/new_show.html', form=form)

    new_show = Show(artist_id=artist_id,
                    venue_id=venue_id, start_time=start_time)

    error = False
    try:
        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

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
