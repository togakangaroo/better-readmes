from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('TodoItem', backref='todo_list', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TodoList {self.name}>'

    @property
    def can_be_deleted(self):
        """Check if list can be deleted (only DONE items or no items)"""
        return all(item.status == 'DONE' for item in self.items)

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='TODO')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)

    status_changes = db.relationship('StatusChange', backref='item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TodoItem {self.title}>'

class StatusChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('todo_item.id'), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<StatusChange {self.old_status} -> {self.new_status}>'
