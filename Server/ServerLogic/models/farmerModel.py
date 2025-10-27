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