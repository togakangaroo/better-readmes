from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object('config')

# Try to load instance config if it exists
try:
    app.config.from_pyfile('instance/config.py')
except FileNotFoundError:
    pass

from models import db, TodoList, TodoItem, StatusChange
from forms import CreateListForm, CreateItemForm, EditItemForm

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

@app.route('/')
def index():
    lists = TodoList.query.all()
    return render_template('index.html', lists=lists)

@app.route('/create_list', methods=['GET', 'POST'])
def create_list():
    form = CreateListForm()
    if form.validate_on_submit():
        todo_list = TodoList(name=form.name.data)
        db.session.add(todo_list)
        db.session.commit()
        flash('List created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_list.html', form=form)

@app.route('/list/<int:list_id>')
def list_detail(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    return render_template('list_detail.html', todo_list=todo_list)

@app.route('/list/<int:list_id>/add_item', methods=['GET', 'POST'])
def add_item(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    form = CreateItemForm()
    if form.validate_on_submit():
        item = TodoItem(
            title=form.title.data,
            status='TODO',
            list_id=list_id
        )
        db.session.add(item)
        db.session.flush()  # Get the item ID
        
        # Create initial status change log
        status_change = StatusChange(
            item_id=item.id,
            old_status=None,
            new_status='TODO',
            timestamp=datetime.utcnow()
        )
        db.session.add(status_change)
        db.session.commit()
        
        flash('Item added successfully!', 'success')
        return redirect(url_for('list_detail', list_id=list_id))
    return render_template('edit_item.html', form=form, todo_list=todo_list, item=None)

@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    form = EditItemForm(obj=item)
    
    if form.validate_on_submit():
        old_status = item.status
        item.title = form.title.data
        item.status = form.status.data
        
        # Log status change if it changed
        if old_status != item.status:
            status_change = StatusChange(
                item_id=item.id,
                old_status=old_status,
                new_status=item.status,
                timestamp=datetime.utcnow()
            )
            db.session.add(status_change)
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('list_detail', list_id=item.list_id))
    
    return render_template('edit_item.html', form=form, todo_list=item.todo_list, item=item)

@app.route('/item/<int:item_id>/change_status', methods=['POST'])
def change_status(item_id):
    item = TodoItem.query.get_or_404(item_id)
    new_status = request.form.get('status')
    
    if new_status in ['TODO', 'IN_PROGRESS', 'DONE']:
        old_status = item.status
        item.status = new_status
        
        # Log status change
        if old_status != new_status:
            status_change = StatusChange(
                item_id=item.id,
                old_status=old_status,
                new_status=new_status,
                timestamp=datetime.utcnow()
            )
            db.session.add(status_change)
        
        db.session.commit()
        flash('Status updated successfully!', 'success')
    
    return redirect(url_for('list_detail', list_id=item.list_id))

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    list_id = item.list_id
    
    # Delete associated status changes first
    StatusChange.query.filter_by(item_id=item_id).delete()
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('list_detail', list_id=list_id))

@app.route('/list/<int:list_id>/delete', methods=['POST'])
def delete_list(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    
    # Check if list can be deleted (only DONE items or no items)
    items = todo_list.items
    if items and any(item.status in ['TODO', 'IN_PROGRESS'] for item in items):
        flash('Cannot delete list with TODO or IN PROGRESS items!', 'error')
        return redirect(url_for('list_detail', list_id=list_id))
    
    # Delete all status changes for items in this list
    for item in items:
        StatusChange.query.filter_by(item_id=item.id).delete()
    
    # Delete all items in the list
    TodoItem.query.filter_by(list_id=list_id).delete()
    
    # Delete the list
    db.session.delete(todo_list)
    db.session.commit()
    
    flash('List deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
