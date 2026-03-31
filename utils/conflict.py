from models.event import Event


def find_conflict(api_key_id, start_time, end_time, exclude_id=None): 
    query = Event.query.filter( 
    Event.api_key_id == api_key_id, 
    Event.start_time < end_time, 
    Event.end_time > start_time 
    ) 
    if exclude_id: 
        query = query.filter(Event.id != exclude_id) 
    return query.first() 

