# imports
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# here is Venue, Artist and show models
# Class Venue information
class Venue (db.Model):
    __tablename__ = 'venues'
    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(100))
    city_name = db.Column(db.String(100))
    state = db.Column(db.String(100))
    address = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    image_link = db.Column(db.String(500))
    # implement any missing fields, as a database migration using Flask-Migrate
    generes = db.Column(db.String(150), nullable=False)
    website = db.Column(db.String(150))
    seek_talent = db.Column(db.Boolean, default=False)
    facebook_link = db.Column(db.String(150))
    seek_description = db.Column(db.Text)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
        return f'{self.venue_name} -{self.address} - {self.generes} '

# Artist information
class Artists(db.Model):
    __tablename__ = 'artists'
    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100), nullable=False)
    city_name = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    generes = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(200))
    # implementing missing fields as a database migration using flask migrate
    website = db.Column(db.String(120))
    seek_venue = db.Column(db.Boolean, default=False)
    seek_description = db.Column(db.Text)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    num_past_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='artists', lazy=True)

    def __repr__(self):
        return f'{self.artist_name}  - {self.city_name} - {self.generes}'
# Implement Shows and Artist models and complete all model relationship and properties, as a database migration
class Show(db.Model):
    __tablename__ = 'shows'
    show_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.venue_id'), nullable=False)
    upcoming_shows = db.Column(db.Boolean, nullable=False, default=True)
    
