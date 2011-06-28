import os

def search_for_calendars():

    calendars = []
    
    calendars.extend(find_evolution_calendars())
    
    return calendars
    
    

def find_evolution_calendars():

    import evolution
    
    calendars = []
    base_path = os.path.join(os.environ['XDG_DATA_HOME'], 'evolution/calendar')
    
    for name, path in evolution.ecal.list_calendars():
        path = path.replace('local:', '')
        path = os.path.join(base_path, path)
        cal_file = os.path.join(path, 'calendar.ics')
        
        if os.path.isfile(cal_file):
            calendar = {'name': name.decode('utf-8'),
                        'source': cal_file,
                        'type': 'evolution'}
            calendars.append(calendar)
            
    return calendars
