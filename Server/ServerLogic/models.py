from ServerLogic import db
from datetime import datetime

class Farmer(db.Model):
    """
    Farmers table model.
    Stores farmer information including ID, phone, and secret key.
    """
    __tablename__ = 'farmers'
    
    # Primary key - Auto-incrementing ID
    id = db.Column(db.Integer, primary_key=True)
    
    # Phone number - Unique and required
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Secret key for authentication
    secret_key = db.Column(db.String(255), nullable=False)
    
    # Metadata fields (good practice)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # String representation
    def __repr__(self):
        return f'<Farmer {self.id}: {self.phone}>'
    
    # Convert to dictionary (useful for JSON responses)
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
            # Note: We don't include secret_key for security
        }
    
class Advisory(db.Model):
    """
    Advisories table model.
    Stores farming advisories/tips that can be sent to farmers.
    """
    __tablename__ = 'advisories'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Advisory content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)  # Text for longer messages
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One advisory can be sent to many farmers
    farming_advisories = db.relationship('FarmingAdvisory', backref='advisory', lazy=True)
    
    def __repr__(self):
        return f'<Advisory {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FarmingAdvisory(db.Model):
    """
    FarmingAdvisories junction table.
    Links farmers to advisories they've received, tracks delivery status.
    """
    __tablename__ = 'farming_advisories'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    advisory_id = db.Column(db.Integer, db.ForeignKey('advisories.id'), nullable=False)
    
    # Delivery tracking
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships - backref creates reverse relationships
    farmer = db.relationship('Farmer', backref='farming_advisories')
    # advisory relationship is created by backref in Advisory model
    
    def __repr__(self):
        return f'<FarmingAdvisory {self.id}: Farmer {self.farmer_id} -> Advisory {self.advisory_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'advisory_id': self.advisory_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'verified': self.verified
        }