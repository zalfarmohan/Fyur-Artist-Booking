import dateutil.parser
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import os
from forms import VenueForm,ArtistForm, ShowForm
import babel
from logging import Formatter, FileHandler
import logging

# importing models, Venue, Artists, and Show
from models import Venue, Show, Artists, db

# App configuration
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# Todo: connection to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:farhanmadka@localhost:5432/myfyyur_db'
# Models


# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime



# here is controllers
@app.route('/')
def index():
    top_ten_artists = Artists.query.order_by(db.desc(Artists.artist_id)).limit(10).all()
    top_ten_venues = Venue.query.order_by(db.desc(Venue.venue_id)).limit(10).all()
    return render_template('pages/home.html',artists=top_ten_artists, venues=top_ten_venues)

# Registering / Create Venue
@app.route('/venues/create', methods=['GET'])
def register_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    create_venue = Venue()
    create_venue.venue_name = request.form['venue_name']
    create_venue.city_name = request.form['city_name']
    create_venue.state = request.form['state']
    create_venue.address = request.form['address']
    create_venue.phone = request.form['phone']
    create_venue.facebook_link = request.form['facebook_link']
    create_venue.generes = request.form['generes']
    create_venue.website = request.form['website']
    create_venue.image_link = request.form['image_link']
    create_venue.seek_description = request.form['seek_description']
    try:
        db.session.add(create_venue)
        db.session.commit()
        # on successfully db insert, flash success
        flash('[- '+request.form['venue_name'] + ' -] successfully created')
    except:
        db.session.rollback()
        # on unsuccessfuly db insert, flash an error instead
        flash('Error occoured, [- '+request.form['venue_name'] +' -] could not created')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))
# display venue with their id
@app.route('/venues/<int:venue_id>')
def display_venues(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venues = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    shows = venues.shows
    for show in shows:
        display_show = {
            'artist_id':show.artist_id,
            'artist_name': show.venues.venue_name,
            'artist_image': show.venues.image_link,
            'start_time': str(show.start_time)
        }
        if show.upcoming_shows:
            upcoming_shows.append(display_show)
        else:
            past_shows.append(display_show)
    data = {
        'venue_id': venues.venue_id,
        'venue_name': venues.venue_name,
        'city_name': venues.city_name,
        'phone': venues.phone,
        'state': venues.state,
        'website': venues.website,
        'seek_description': venues.seek_description,
        'image_link': venues.image_link,
        'past_show': past_shows,
        'upcomming_shows': upcoming_shows,
        'num_shows': len(past_shows),
        'num_upcomming_shows': len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)


# show venues
@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue
    all_venues_area = db.session.query(Venue.city_name, Venue.state).group_by(Venue.state, Venue.city_name).all()
    data = Venue.query.with_entities(Venue.venue_id, Venue.venue_name, Venue.city_name, Venue.state).all()
    data= []
    for area in all_venues_area:
        venues = db.session.query(Venue.venue_id, Venue.venue_name,
        Venue.num_upcoming_shows).filter(Venue.city_name==area[0], Venue.state==area[1]).all()
        data.append({
            'city_name':area[0],
            'state': area[1],
            'venues':[]
        })
        for venue in venues:
            data[-1]['venues'].append({
                'id':venue[0],
                'venue_name':venue[1],
                'upcomming_shows':venue[2]
            })
    return render_template('pages/venues.html', areas=data)



# update venues
@app.route('/venues/edit', methods=['GET'])
def update_venues():
    venue_id = request.args.get('venue_id')
    venue_form = VenueForm()
    venues = Venue.query.get(venue_id)
    venue_info = {
        'venue_id': venues.venue_id,
        'venue_name': venues.venue_name,
        'address': venues.address,
        'phone': venues.phone,
        'generes': venues.generes,
        'image_link': venues.image_link,
        'city_name': venues.city_name,
        'state': venues.state,
    }
    return render_template('forms/edit_venue.html', form=venue_form, venue=venue_info)

# update submission venue
@app.route('/venues/<int:venue_id>/edit',methods=['POST'])
def update_venueSubmition(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue_update = Venue.query.get(venue_id)
    venue_update.venue_name = request.form['venue_name']
    venue_update.city_name = request.form['city_name']
    venue_update.state = request.form['state']
    venue_update.address = request.form['address']
    venue_update.phone = request.form['phone']
    venue_update.website = request.form['website']
    venue_update.image_link = request.form['image_link']
    venue_update.generes = request.form['generes']
    try:
        db.session.commit()
        flash('Venue [- '+ request.form['venue_name']+ ' -] has been updated successfully')
    except:
        db.session.rollback()
        flash(' [- '+request.form['venue_name'] + ' -] failed to updated try again!!!!!!!')
    finally:
        db.session.close()
    return redirect(url_for('index'))
    

# end update venue

# delete permanently venue records
@app.route('/venues/delete', methods=['POST'] )
def delete_venueRecords():
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail@app.route("route")
    venue_no = request.form.get('venue_id')
    deleterecord = Venue.query.get(venue_no)
    name = deleterecord.venue_name
    try:
        db.session.delete(deleterecord)
        db.session.commit()
        flash('Venue [- ' + name+ ' -] has been deleted sucessfully')
    except:
        db.session.rollback()
        flash('Venue [- ' + name+ ' -] can not be deleted. Delete child table first')
    finally:
        db.session.close()
    return redirect(url_for('index'))
# show artists
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from quering the database
    data = Artists.query.with_entities(Artists.artist_id, Artists.artist_name).all()
    return render_template('pages/artists.html', artists=data)

# indvidual artist by id
@app.route('/artists/<int:artist_id>')
def display_artist(artist_id):
    # show the artist page with the given arist_id
    # TODO: replace with the real artist data from the real artist table using artist_id
    artists = Artists.query.get(artist_id)
    shows = artists.shows
    past_show = []
    upcoming_shows = []
    for show in shows:
        show_info = {
            'venue_id':show.venue_id,
            'venue_name':show.artists.artist_name,
            'venue_image_link':show.artists.image_link,
            'start_time':str(show.start_time)
        }
        if show.upcoming_shows:
            upcoming_shows.append(show_info)

        else:
            past_show.append(show_info)
    data = {
        'artist_id':artists.artist_id,
        'artist_name': artists.artist_name,
        'city_name':artists.city_name,
        'state':artists.state,
        'generes':artists.generes.split(','),
        'phone':artists.phone,
        'website':artists.website,
        'facebook_link':artists.facebook_link,
        'seek_venue':artists.seek_venue,
        'seek_description':artists.seek_description,
        'image_link':artists.image_link,
        'past_shows':upcoming_shows,
        'past_shows_count':len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)





# artist form
@app.route('/artists/create', methods=['GET'])
def register_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html',form = form)

# Artist submission
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Called upon sumitting the nwe artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    save_artist = Artists()
    save_artist.artist_name = request.form['artist_name']
    save_artist.city_name = request.form['city_name']
    save_artist.state = request.form['state']
    save_artist.address = request.form['address']
    save_artist.phone = request.form['phone']
    save_artist.facebook_link = request.form['facebook_link']
    save_artist.generes = request.form['generes']
    save_artist.website = request.form['website']
    save_artist.image_link = request.form['image_link']
    save_artist.seek_description = request.form['seek_description']
    try:
        db.session.add(save_artist)
        db.session.commit()
        flash('[- '+request.form['artist_name'] + ' -] has been listed successfully')
    except:
        db.session.rollback()
        # if failed
        flash('An error occored. Artist [- '+request.form['artist_name'] + ' -] could not be listed')
    finally:
        db.session.close()
    return redirect(url_for('index'))
# end artist submission

# start artist update
@app.route('/artists/edit', methods=['GET'])
def update_artists():
    update_form = ArtistForm()
    artist_id = request.args.get('artist_id')
    artists= Artists.query.get(artist_id)
    artists_display ={
        'artist_id': artists.artist_id,
        'artist_name': artists.artist_name,
        'city_name': artists.city_name,
        'state': artists.state,
        'phone': artists.phone,
        'address': artists.address,
        'generes': artists.generes.split(','),
        'website': artists.website,
        'facebook_link': artists.facebook_link,
        'seek_venue':artists.seek_venue,
        'seek_description': artists.seek_description,
        'image_link':artists.image_link
    }
    return render_template('forms/edit_artist.html', form=update_form, artist=artists_display)

# update submission
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def update_artist_form(artist_id):
    # TODO: take values from the form submitted, and update existing
    # Artist record with ID <artist_id> using the new attributes
    update_artist = Artists.query.get(artist_id)
    update_artist.artist_name = request.form['artist_name']
    update_artist.city_name = request.form['city_name']
    update_artist.state = request.form['state']
    update_artist.phone = request.form['phone']
    update_artist.address = request.form['address']
    update_artist.generes = request.form['generes']
    update_artist.website = request.form['website']
    update_artist.facebook_link = request.form['facebook_link']
    update_artist.seek_description = request.form['seek_description']
    update_artist.image_link = request.form['image_link']
    try:
        db.session.commit()
        # if it's true artist should be updated
        flash('[- '+reqiest.form['artist_name'] + ' -] Artist  has been updated successfully')
    except:
        # else if its' not true artist failed
        db.session.rollback()
        flash('Artist  Failed to update!!!')
    finally:
        db.session.close()
    return redirect(url_for('display_artist', artist_id=artist_id))

    
    
# end artist update
@app.route('/artists/delete', methods=['POST'])
def delete_artists():
    artists_id = request.form.get('artist_id')
    del_artists = Artists.query.get(artists_id)
    artists_name = del_artists.artist_name
    try:
        db.session.delete(delete_artists)
        db.session.commit()
        flash('Artist [- '+artists_name+ ' -] has been deleted successfully')
    except:
        db.session.rollback()
        flash('Sorry could not be deleted try it again. delete child table first')
    finally:
        db.session.close()
    return redirect(url_for('index'))

# delete artists

# end delete artists

# shows
@app.route('/shows')
def shows():
    # display list of shows at /shows
    # Todo: replace with real venue data. num_shows should be aggregated basaed on number of upcoming shows per artist
    all_shows = Show.query.all()
    data = []
    for show in all_shows:
        if (show.upcoming_shows):
            data.append({
                'venue_id': show.venue_id,
                'venue_name': show.venues.venue_name,
                'artist_id': show.artist_id,
                'artist_name': show.artists.artist_name,
                'artist_image': show.artists.image_link,
                'start_time': str(show.start_time)
            })
    return render_template('pages/shows.html', shows=data)

# form show
@app.route('/shows/create')
def register_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
# show submission
@app.route('/shows/create', methods=['POST'])
def show_submission():
    # called to create new shows in the db, upon submitting new show list form
    # TODO: insert form data as a new show record in the db, instead
    save_shows = Show()
    save_shows.artist_id = request.form['artist_id']
    save_shows.venue_id = request.form['venue_id']
    current_time = request.form['start_time'].split(' ')
    DTList  = current_time[0].split('-')
    DTList += current_time[1].split(':')
    for i in range(len(DTList)):
        DTList[i] = int(DTList[i])
    save_shows.start_time = datetime(DTList[0],DTList[1],DTList[2],DTList[3],DTList[4],DTList[5])
    now = datetime.now()
    save_shows.upcoming_shows = (now < save_shows.start_time)
    try:
        db.session.add(save_shows)
        # update venue and artist table
        artists = Artists.query.get(save_shows.artist_id)
        venues = Venue.query.get(save_shows.venue_id)
        if save_shows.upcoming_shows:
            artists.num_upcoming_shows +=1
            venues.num_upcoming_shows +=1
        else:
            artists.num_past_shows +=1
            venues.num_upcoming_shows +=1
        # On successful db insert, flash success
        db.session.commit()
        flash('Show was listed successfully.')
    except:
        db.session.rollback()
        # Todo: on unsuccessful db insert, flash an error instead
        flash('Show could not be listed please check your ids')
    finally:
        db.session.close()
    return redirect(url_for('index'))




# finding specific column
@app.route('/venues/search', methods=['POST'])
def venue_search():
    # TODO: implement search on artists with partial string search. Ensures it is case-insensitive.
    # Search for HOP should reutn 'The musical Hop'.
    # search for "Music" should return "The Musical Hop" and Park Square Live Music & Coffee"
    result_venues = Venue.query.filter(Venue.venue_name.ilike('%{}'.format(request.form['search_term']))).all()
    result = {
        'count':len(result_venues),
        'data':[]
    }
    for venue in result_venues:
        result['data'].append({
            'venue_id': venue.venue_id,
            'venue_name': venue.venue_name,
            'num_upcomingshows':venue.num_upcoming_shows
        })
    return render_template('pages/search_venues.html',results=result, search_term=request.form.get('search_term',''))

# finding specific column
@app.route('/artists/search', methods=['POST'])
def artist_search():
    result_artists = Artists.query.filter(Artists.artist_name.ilike('%{}'.format(request.form['search_term']))).all()
    result = {
        'count':len(result_artists),
        'data':[]
    }
    for artist in result_artists:
        result['data'].append({
            'artist_id': artist.artist_id,
            'artist_name': artist.artist_name,
            'num_upcommingshows': artist.num_upcoming_shows
        })
    return render_template('pages/search_artists.html',results=result, search_term=request.form.get('search_term',''))
# default port
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# default port
if __name__ == '__main__':
    app.run()

# specific port
if __name__ == "__main__":
    port =  int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0',port=port, debug=True)